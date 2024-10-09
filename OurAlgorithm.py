import scipy.sparse as sp
import time
import numpy as np
from numpy.linalg import norm
EPSILON = np.finfo(np.float32).eps
import numpy as np
start_total = time.time()



def normalize_matrix(matrix):
    total_sum = matrix.sum()
    if total_sum == 0:
        return matrix  # Avoid division by zero
    return matrix / total_sum


def normalize(matrix):
    norm_factors = np.linalg.norm(matrix, axis=1, keepdims=True)
    norm_factors[norm_factors == 0] = 1
    return matrix / norm_factors


def safe_sparse_dot(a, b, *, dense_output=False):
    if a.ndim > 2 or b.ndim > 2:
        if sp.issparse(a):
            # sparse is always 2D. Implies b is 3D+
            # [i, j] @ [k, ..., l, m, n] -> [i, k, ..., l, n]
            b_ = np.rollaxis(b, -2)
            b_2d = b_.reshape((b.shape[-2], -1))
            ret = a @ b_2d
            ret = ret.reshape(a.shape[0], *b_.shape[1:])
        elif sp.issparse(b):
            # sparse is always 2D. Implies a is 3D+
            # [k, ..., l, m] @ [i, j] -> [k, ..., l, j]
            a_2d = a.reshape(-1, a.shape[-1])
            ret = a_2d @ b
            ret = ret.reshape(*a.shape[:-1], b.shape[1])
        else:
            ret = np.dot(a, b)
    else:
        ret = a @ b

    if (
            sp.issparse(a)
            and sp.issparse(b)
            and dense_output
            and hasattr(ret, "toarray")
    ):
        return ret.toarray()
    return ret

def _special_sparse_dot(W, H, X):
    """Computes np.dot(W, H), only where X is non zero."""
    if sp.issparse(X):
        ii, jj = X.nonzero()
        n_vals = ii.shape[0]
        dot_vals = np.empty(n_vals)
        n_components = W.shape[1]

        batch_size = max(n_components, n_vals // n_components)
        for start in range(0, n_vals, batch_size):
            batch = slice(start, start + batch_size)
            dot_vals[batch] = np.multiply(W[ii[batch], :], H.T[jj[batch], :]).sum(axis=1)
        WH = sp.coo_matrix((dot_vals, (ii, jj)), shape=X.shape)
        return WH.tocsr()
    else:
        return np.dot(W, H)


def _initialize_mmatrix(V, n_topics):
    m, n = V.shape
    W = np.abs(np.random.randn(m, n_topics) * 0.01)
    H = np.abs(np.random.randn(n_topics, n) * 0.01)
    return W, H

def kl_divergence(V, W, H):
    if sp.issparse(V):
        # compute np.dot(W, H) only where X is nonzero
        WH_data = _special_sparse_dot(W, H, V).data
        V_data = V.data
    else:
        WH = np.dot(W, H)
        WH_data = WH.ravel()
        V_data = V.ravel()

    indices = V_data > EPSILON
    WH_data = WH_data[indices]
    V_data = V_data[indices]
    # used to avoid division by zero
    WH_data[WH_data < EPSILON] = EPSILON

    V_data[V_data < EPSILON] = EPSILON

    sum_WH = np.dot(np.sum(W, axis=0), np.sum(H, axis=1))
    # computes np.sum(X * log(X / WH)) only where X is nonzero
    div = V_data / WH_data
    res = np.dot(V_data, np.log(div))
    # add full np.sum(np.dot(W, H)) - np.sum(X)
    res += sum_WH - V_data.sum()
    #return res

    num_documents = V.shape[0]
    num_vocab_terms = V.shape[1]
    return res / (num_documents * num_vocab_terms)



def g1( V, W, MH_indices, seed_indices, W_max):
    doc_seedword_sums = np.sum(V[:, seed_indices], axis=1)
    zero_seedword_indices = np.where(doc_seedword_sums == 0)[0]
    W[zero_seedword_indices[:, np.newaxis], MH_indices] = np.minimum(W[zero_seedword_indices[:, np.newaxis], MH_indices], W_max)
    return W


def g2(H, seed_indices, theta_min):
    num = np.sum(H[:, seed_indices], axis=1)
    den = np.sum(H, axis=1)
    g2_value = theta_min - (num / den)
    return g2_value


def gradient_W(V, W, H, lambda_, MH_indices, W_max, zero_seed_indices):
    WH = np.dot(W, H)
    V_WH = V / (WH)
    term1 = safe_sparse_dot(V_WH, H.T)
    term2 = safe_sparse_dot(np.ones(V.shape), H.T)
    if term1.shape != W.shape:
        raise ValueError(f"Dimension mismatch: term1 shape {term1.shape}, W shape {W.shape}")
    if term2.shape != W.shape:
        raise ValueError(f"Dimension mismatch: term2 shape {term2.shape}, W shape {W.shape}")
    grad_W = term2 - term1
    num_documents = V.shape[0]
    num_vocab_terms = V.shape[1]
    return grad_W / (num_documents * num_vocab_terms)

def gradient_H(V, W, H, mu, seed_indices, theta_min):
    WH = np.dot(W, H)
    V_WH = V / (WH)
    term1 = safe_sparse_dot(W.T, V_WH)
    term2 = safe_sparse_dot(W.T, np.ones(V.shape))
    if term1.shape != H.shape:
        raise ValueError(f"Dimension mismatch: term1 shape {term1.shape}, H shape {H.shape}")
    if term2.shape != H.shape:
        raise ValueError(f"Dimension mismatch: term2 shape {term2.shape}, H shape {H.shape}")
    grad_H = term2 - term1
    num_documents = V.shape[0]
    num_vocab_terms = V.shape[1]
    return grad_H / (num_documents * num_vocab_terms)


def update_W(V, W, H, lambda_, MH_indices, zero_seed_indices):
    WH = np.dot(W, H)
    positive_term = safe_sparse_dot(V / WH, H.T)
    negative_term = safe_sparse_dot(np.ones(V.shape), H.T)
    g1_W = np.zeros_like(W)
    for i in zero_seed_indices:
        if i < W.shape[0]:
            g1_W[i, MH_indices] = 1

    W *= positive_term / (negative_term + lambda_ * g1_W)
    W= np.clip(W, 1e-12, None)
    return W


def update_H(V, W, H, mu, seed_indices, MH_indices):
    WH = np.dot(W, H)
    positive_term = safe_sparse_dot(W.T, V / WH)
    negative_term = safe_sparse_dot(W.T, np.ones(V.shape))
    num = np.sum(H[:, seed_indices], axis=1, keepdims=True)
    den = np.sum(H, axis=1, keepdims=True)
    g2_term = np.zeros_like(H)
    for k in range(H.shape[0]):
        if k in MH_indices:
            g2_term[k, seed_indices] = -((den[k] - num[k]) / (den[k] ** 2))
    H *= positive_term / (negative_term + mu * g2_term)
    H= np.clip(H, 1e-12, None)
    return H


def update_lambda(V, lambda_, W, MH_indices, seed_indices, W_max, eta):
    g1_val = g1(V, W, MH_indices, seed_indices, W_max)
    lambda_ = np.maximum(0, lambda_ + eta * g1_val)
    lambda_[g1_val < 0] = 0
    return lambda_

def update_mu(mu, H, seed_indices, theta_min, eta):
    g2_val = g2(H, seed_indices, theta_min)
    g2_val_expanded = g2_val[:, np.newaxis]
    mu_update = mu + eta * g2_val_expanded
    mu = np.maximum(0, mu_update)
    mu[g2_val < 0] = 0
    return mu


# Track gradient norms
def frobenius_norm(matrix):
    return np.linalg.norm(matrix, 'fro')

def train(V, n_topics, MH_indices, W_max, zero_seed_indices, seed_indices, theta_min, max_iter=100, tol=1e-4):
    m, n = V.shape
    W, H = _initialize_mmatrix(V, n_topics)
    lambda_ = np.zeros(W.shape)
    mu = np.zeros(H.shape)
    kl_losses = []
    grad_W_norms = []
    grad_H_norms = []
    for i in range(max_iter):

        kl_loss = kl_divergence(V, W, H)
        kl_losses.append(kl_loss)
        grad_W = gradient_W(V, W, H, lambda_, MH_indices, W_max, zero_seed_indices)
        grad_H = gradient_H(V, W, H, mu, seed_indices, theta_min)

        grad_W_norms.append(frobenius_norm(grad_W))
        grad_H_norms.append(frobenius_norm(grad_H))



        assert W.shape[1] == H.shape[0], f"Dimension mismatch: W.shape[1] = {W.shape[1]}, H.shape[0] = {H.shape[0]}"
        if i % 2 == 0:
            print(f'Iteration {i}, KL Divergence: {kl_loss}')

        W = update_W(V, W, H, lambda_, MH_indices, zero_seed_indices)
        H = update_H(V, W, H, mu, seed_indices, MH_indices)
        lambda_ = update_lambda(V, lambda_, W, MH_indices, seed_indices, W_max, eta=0.001)
        mu = update_mu(mu, H, seed_indices, theta_min, eta=0.001)
        # Stopping criterion based on tolerance (using KL divergence)
        if kl_loss < tol:
            print(f"Converged at iteration {i}, KL Divergence: {kl_loss}")
            break

    W = normalize_matrix(W)
    H = normalize_matrix(H)

    return W, H







