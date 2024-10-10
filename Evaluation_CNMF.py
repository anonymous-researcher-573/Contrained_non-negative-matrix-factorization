import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF
from sklearn.decomposition import LatentDirichletAllocation
import nltk
import guidedlda
from gensim import corpora
from sklearn.metrics import normalized_mutual_info_score
from gensim.models.coherencemodel import CoherenceModel
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from top2vec import Top2Vec
from corextopic import corextopic as ct
from OurAlgorithm import *
from collections import defaultdict, Counter



def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('finnish'))
    tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    return tokens

data = pd.read_csv('./synthetic-data.csv')
documents = data['Sentence'].astype(str)
true_labels = data['Label'].tolist()  # If available

processed_docs = documents.apply(preprocess_text)
dictionary = corpora.Dictionary(processed_docs)
corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
documents = processed_docs.apply(lambda x: ' '.join(x))
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
tfidf_feature_names = tfidf_vectorizer.get_feature_names_out()


seed_words =[
    "terapeutti",
    "negatiivisuus",
    "depressio",
    "paniikkikohtaus",
    "terapeutti",
    "tunne",
    "positiivisuus",
    "onnellisuus",
    "motivaatio",
    "tasapaino",
    "selkeys",
    "mielenrauha",
    "itsetunto",
    "itseluottamus",
    "ahdistus",
    "masennus",
    "yksinäisyys",
    "epävarmuus",
    "pelko",
    "stressitaso",
    "stressihäiriö",
    "stressitön",
    "stressihormo",
    "mielenterveysongelma",
    "skitsofreenikko",
    "terapia",
    "psykoterapia",
    "lääkäri",
    "neuvonta",
    "tuki",
    "keskustelu",
    "ystävät",
    "perhe",
    "epätoivo",
    "viha",
    "pelko",
    "häpeä",
    "turhautuminen",
    "ahdistuskohtaus",
    "itku",
    "toipuminen",
    "paraneminen",
    "edistyminen",
    "itsehoito",
    "rentoutuminen",
    "hengitellä",
    "chillaa",
    "voimaantuminen",
    "neuvo",
    "jutella",
    "kipu",
    "hullu",
    "hoito",
    "ilo",
    "ärsyttävä",
    "pelastua",
    "heikkous",
    "huume",
    "lepo",
    "odotus",
    "kriisitila",
    "epäsosiaalinen",
    "yhteisöllisyys",
    "psyko",
    "huolestua",
    "väsymys",
    "neuropsykologia",
    "arvostelukyky",
    "ihmissuhde",
    "terveydellinen",
    "Asperger",
    "kuunnella",
    "itsemurha",
    "käyttäytymishäiriö",
    "autismi",
    "ahdistuneisuushäiriö",
    "paniikki",
    "eristäytyminen",
    "yksinäisyys",
    "adhd",
    "anoreksia",
    "bulimia",
    "mielenterveyshäiriö",
    "hallusinaatio",
    "harhaluulo",
    "luottaa",
    "väärinkäyttö",
    "kannabis",
    "väkivalta",
    "lihavuus",
    "kärsimys",
    "itsetuhoisuus",
    "sairaus",
    "paniikkihäiriö",
    "ahdistuneisuushäiriö",
    "ocd",
    "depressio",
    "tarkkaavaisuushäiriö",
    "syömishäiriöt",
    "skitsofrenia",
    "hallusinaatioita",
    "ptsd",
    "toivoton",
    "huolestunut",
    "surullinen",
    "tukea",
    "apua",
    "uupumus",
    "trauma",
    "paniikkikohtaus",
    "psykoterapia",
    "jooga",
    "meditaatio",
    "psykiatria",
    "sairaalahoito",
    "itsehoito",
    "kriisiapu",
    "kriisipuhelin",
    "tukiryhmä"
    "serotoniinivajaus",
    'addiktio',
    'alakulo',
    'burnout',
    'elämänhallinta',
    'erot',
    'häirintä',
    'häpeä',
    'ihmissuhteet',
    'itseinho',
    'itsemyötätunto',
    'itsetuhoisuus',
    'julkisuus',
    'jännittäminen',
    'kateus',
    'kehonkuva',
    'kiitollisuus',
    'kiusaaminen',
    'lapsettomuus',
    'maskaaminen',
    'mielenterveys',
    'multimodaalisuus',
    'päihteet',
    'stigma',
    'stressi',
    'syrjäytyminen',
    'syömishäiriö',
    'terapia',
    'ulkonäkö',
    'uupumus',
    'vaikuttaminen',
    'vertaistuki',
    'vihapuhe',
    'vuorovaikutus',
    'yksinäisyys',
    'ylikontrolli',
    'ylisuorittaminen'
    "tunteet",
    "mindstorm"
    "rakkaus",
    "surumielisyys",
    "onnellisuus",
    "ilonaihe",
    "pettymys",
    "empatia",
    "psykoosi",
    "epäluuloisuus",
    "psyykkinen trauma",
    "ajatushäiriö",
    "persoonallisuushäiriö",
    "psykopaattisuus",
    "kehotietoisuus",
    "itsetutkiskelu",
    "hyvinvointivalmennus",
    "terapiasuositus",
    "elämäntapamuutos",
    "resilienssi",
    "rentoutumistekniikat",
    "itsesäätely",
    "stressinhallinta",
    "tunnereaktio",
    "perhesuhteet",
    "ryhmäterapia",
    "suhdeongelmat",
    "aivokemia",
    "unihäiriöt",
    "aivotoiminta",
    "fysiologinen",
    "ensiapu",
    "hätäapu",
    "voimaannuttaminen",
    "skitsoaffektiivisesta",
    "kriisi",
    "ahdistunut",
    "depressiivinen"

]

seed_word_groups= [seed_words, seed_words, seed_words, seed_words, seed_words, seed_words, seed_words]

#initialize Our Algorithm
seed_indices = [i for i, word in enumerate(tfidf_feature_names) if word in set(seed_words)]
non_seed_indices = [i for i in range(len(tfidf_feature_names)) if i not in seed_indices]
print("number of seed words in vocab: %d" % len(seed_indices))
n_topics=20
W_max=1e-9
theta_min=0.4
MH_indices=[0, 1, 2, 3, 4, 5, 6]
W, H = train(tfidf_matrix, n_topics, MH_indices, W_max, non_seed_indices, seed_indices, theta_min, max_iter=20)





anchors = [
    [a for a in topic if a in tfidf_feature_names]
    for topic in seed_word_groups
]
corexi_model = ct.Corex(n_hidden=n_topics, seed=42)
corex_model = corexi_model.fit(
    tfidf_matrix,
    words=tfidf_feature_names,
    anchors=anchors,
    anchor_strength= 40

)

# Initialize NMF model
nmf_model = NMF(n_components=n_topics, random_state=42)
nmf_model.fit(tfidf_matrix)
nmf_topics = nmf_model.components_




# Initialize LDA model
lda_model = LatentDirichletAllocation(n_components=n_topics, random_state=42)
lda_model.fit(tfidf_matrix)
lda_topics = lda_model.components_




vectorizer = CountVectorizer()
bow_matrix = vectorizer.fit_transform(documents)
tfidf_feature_names_guided = vectorizer.get_feature_names_out()

guided_model = guidedlda.GuidedLDA(n_topics=n_topics, n_iter=100, random_state=42, refresh=20)
word2id = {word: i for i, word in enumerate(tfidf_feature_names_guided)}

seed_topics = {}
for t_id, st in enumerate(seed_word_groups):
    for word in st:
        if word in word2id:
            seed_topics[word2id[word]] = t_id
guided_model.fit(bow_matrix, seed_topics=seed_topics, seed_confidence=0.4)
n_top_words = 15
topic_word = guided_model.topic_word_
topic_words_list = []
print("\nGuided LDA Topics:")
for i, topic_dist in enumerate(topic_word):
    top_word_ids = np.argsort(topic_dist)[-n_top_words:][::-1]  # descending order
    top_words = [tfidf_feature_names_guided[word_id] for word_id in top_word_ids]
    topic_words_list.append(top_words)  # Store words for each topic
    print('Topic {}: {}'.format(i, ', '.join(top_words)))

documents_list = documents.tolist()

top2vec_model = Top2Vec(documents=documents_list, speed="deep_learn", workers=4)
topic_wordss, word_scores, topic_nums = top2vec_model.get_topics()


print("\nTOP2VEC model Topics: ")
for i, topic in enumerate(topic_nums):
    print(f"Topic {topic}: {', '.join(topic_wordss[i])}")


def get_topicsss(H, top_words, id2word):
    topic_list = []
    for topic in H:
        words_list = sorted(list(enumerate(topic)), key=lambda x: x[1], reverse=True)
        topk = [tup[0] for tup in words_list[:top_words]]
        topk_proportions = [tup[1] for tup in words_list[:top_words]]
        topk_proportions = [x / sum(topk_proportions) for x in topk_proportions]
        topic_list.append([(id2word[i], prop) for i, prop in zip(topk, topk_proportions)])
    return topic_list

top_words= 10
result = {}
result["topic-word-matrix"] = H
id2word = {i: word for i, word in enumerate(tfidf_feature_names)}
if top_words > 0:
    result["topics"] = get_topicsss(H, top_words, id2word)



def get_topics(H, top_words, id2word):
    topic_list = []
    for topic_idx, topic in enumerate(H):
        # Sort the words in the topic by their weight
        words_list = sorted(list(enumerate(topic)), key=lambda x: x[1], reverse=True)
        topk = [tup[0] for tup in words_list[:top_words]]
        topk_words = [id2word[i] for i in topk]
        topic_list.append(topk_words)
        print(f"Topic {topic_idx + 1}: {', '.join(topk_words)}")
    return topic_list





def display_topics(model, feature_names, no_top_words):
    topics = []
    for topic_idx, topic in enumerate(model):
        top_words = [feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]
        topics.append(top_words)
        print(f"Topic {topic_idx+1}: {', '.join(top_words)}")
    return topics

def display_topics_corex(model, no_top_words):
    topics = []
    for i, topic_ngrams in enumerate(model.get_topics(no_top_words)):
        topic_ngrams = [ngram[0] for ngram in topic_ngrams]
        topics.append(topic_ngrams)
        print("Topic #{}: {}".format(i+1, ", ".join(topic_ngrams)))
    return topics













print("\nNMF Topics:")
nmf_topic_words = display_topics(nmf_topics, tfidf_feature_names, 10)
print("\nLDA Topics:")
lda_topic_words = display_topics(lda_topics, tfidf_feature_names, 10)
print("\nCorex Topics:")
corex_topic_words= display_topics_corex(corex_model, 10)
print("\nOur Model Topics:")
own_topic_words = get_topics(H, 10, id2word=id2word)


# NMF Topic Assignments
nmf_doc_topics = nmf_model.transform(tfidf_matrix)
nmf_doc_labels = np.argmax(nmf_doc_topics, axis=1)


# LDA Topic Assignments
lda_doc_topics = lda_model.transform(tfidf_matrix)
lda_doc_labels = np.argmax(lda_doc_topics, axis=1)


# Corex Topic Assignments
cor_doc_topics = corex_model.transform(tfidf_matrix)
cor_doc_labels = np.argmax(cor_doc_topics, axis=1)
#corex_labels = corex_model.labels
#corex_labels = np.argmax(corex_labels, axis=1)

# Our Model Topic Assignments
own_doc_labels = np.argmax(W, axis=1)


# Guided LDA Topic Assignments
guided_lda_doc_topics = guided_model.transform(bow_matrix)
guided_lda_doc_labels = np.argmax(guided_lda_doc_topics, axis=1)



predicted_labels = np.zeros(len(true_labels))
num_topics = len(topic_nums)

for topic_num in range(num_topics):
    num_docs_for_topic = top2vec_model.topic_sizes[topic_num]
    num_docs_to_retrieve = min(len(true_labels), num_docs_for_topic)
    dociiii, document_scores, document_ids = top2vec_model.search_documents_by_topic(
        topic_num=topic_num,
        num_docs=num_docs_to_retrieve
    )
    for doc_id in document_ids:
        predicted_labels[doc_id] = topic_num
predicted_labels = np.array(predicted_labels)

def get_top_documents_corex(model, tfidf_matrix, documents, top_n=5):
    topic_doc_dist = model.p_y_given_x
    top_docs_per_topic = {}
    for topic_idx in range(topic_doc_dist.shape[1]):
        top_doc_indices = np.argsort(topic_doc_dist[:, topic_idx])[::-1][:top_n]
        top_docs = documents.iloc[top_doc_indices].values.tolist()
        top_docs_per_topic[topic_idx] = top_docs

    return top_docs_per_topic

top_docs_corex = get_top_documents_corex(corex_model, tfidf_matrix, processed_docs, 5)
#print(top_docs_corex)

def highlight_top_words(document, top_words):
    if isinstance(document, list):  # Check if document is a list
        document = ' '.join(document)  # Join list into a single string
    highlighted = document
    for word in top_words:
        highlighted = highlighted.replace(word, f'*{word}*')  # Highlight the top words
    return highlighted


def kl_divergence(p, q):
    log_q = np.where(q != 0, np.log(q), -1000)
    Ip = np.where(p != 0)
    return np.sum(p[Ip] * (np.log(p[Ip]) - log_q[Ip]))
def jensen_shannon_divergence(p, q):
    p = np.array(p)
    q = np.array(q)
    p = p / np.sum(p)
    q = q / np.sum(q)
    m = 0.5 * (p + q)
    return 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)

def rank_documents_by_custom_js(V, W, H):

    n_topics = H.shape[0]
    n_docs = W.shape[0]
    ranked_docs = {}

    for topic_index in range(n_topics):
        topic_word_distribution = H[topic_index, :]
        js_divergences = np.zeros(n_docs)

        for doc_index in range(n_docs):
            doc_word_distribution = V[doc_index, :].todense()
            doc_word_distribution = np.array(doc_word_distribution).squeeze()
            js_divergences[doc_index] = jensen_shannon_divergence(doc_word_distribution, topic_word_distribution)
        ranked_docs[topic_index] = np.argsort(js_divergences)

    return ranked_docs

ranked_documents = rank_documents_by_custom_js(tfidf_matrix, W, H)
output_file= './final_output.txt'

with open(output_file, 'w') as file:
    for topic_index in range(n_topics):
        document_indices = ranked_documents[topic_index][:10]
        file.write(f"Top 40 documents for Topic #{topic_index}:\n")
        file.write(f"{document_indices}\n")

        top_words = set(word for word, _ in result["topics"][topic_index])
        for doc_index in document_indices:
            highlighted_doc = highlight_top_words(processed_docs[doc_index], top_words)
            file.write(f"Document #{doc_index}: {highlighted_doc}\n")
    file.write("\nGenerated Topics and Associated Documents:\n")
    for topic_idx, words in enumerate(result["topics"]):
        topic_words = ' - '.join([f"{word}" for word, _ in words])
        file.write(f"Topic #{topic_idx}: {topic_words}\n")

#yzeros= np.zeros(len(documents))
#for i in range(len(documents)):
    #yzeros[i] = np.argmax(W[i, :])
y_true = np.array(true_labels)
#y_pred_m = np.array(yzeros)





# this function calculate purity by grouping predicted clusters and then checking how
# pure each cluster is by finding the most frequent true label within that cluster.
# This is more aligned with standard purity metrics in clustering, where we look at clusters' "purity.

def purity_score_filtered(y_true, y_pred, exclude_labels_from_majority=[], exclude_labels_from_purity=[]):
    cluster_to_labels = defaultdict(list)
    for true_label, cluster in zip(y_true, y_pred):
        cluster_to_labels[cluster].append(true_label)

    total_samples = 0
    total_pure_samples = 0
    for cluster, labels in cluster_to_labels.items():
        label_count = Counter(labels)
        # Count all samples in the cluster, excluding classes not counted for purity
        cluster_samples_count = 0
        for k in label_count:
            if (k in exclude_labels_from_purity)==False:
                cluster_samples_count += label_count[k]

        # Determine the majority class, excluding classes not counted for majority
        for k in exclude_labels_from_majority:
            label_count[k] = 0
        most_common_info = label_count.most_common()
        most_common_label_count = most_common_info[0][1]

        # There might be multiple equally most-common labels, count them all
        most_common_labels=[]
        most_common_label_counts=[]
        for k in range(len(most_common_info)):
            if most_common_info[k][1]==most_common_label_count:
                most_common_labels.append(most_common_info[k][0])
                most_common_label_counts.append(most_common_info[k][1])

        if most_common_label_count==0:
            #print('Skipping cluster' + str(cluster))
            continue

        # Exclude most-common classes not eligible for purity computation
        for k in range(len(most_common_labels)):
            if (most_common_labels[k] in exclude_labels_from_purity)==True:
                most_common_label_counts[k]=0


        total_pure_samples += max(most_common_label_counts)
        total_samples += cluster_samples_count
        #print('Sample counts now: total ' + str(total_samples) + ', pure ' + str(total_pure_samples))

    return total_pure_samples / total_samples





# Convert to a pandas DataFrame for easier handling
unique_labels = np.unique(y_true[y_true != '-1'])
# Create a mapping for labels, starting from 1
label_mapping = {label: idx for idx, label in enumerate(unique_labels, start=1)}
ytrue_example = np.array([label_mapping.get(label, -1) for label in y_true])


nmf_purity = purity_score_filtered(ytrue_example, nmf_doc_labels, exclude_labels_from_majority=[-1], exclude_labels_from_purity=[])
lda_purity = purity_score_filtered(ytrue_example, lda_doc_labels, exclude_labels_from_majority=[-1], exclude_labels_from_purity=[])
cor_purity = purity_score_filtered(ytrue_example, cor_doc_labels, exclude_labels_from_majority=[-1], exclude_labels_from_purity=[])
own_purity = purity_score_filtered(ytrue_example, own_doc_labels, exclude_labels_from_majority=[-1], exclude_labels_from_purity=[])
guided_lda_purity = purity_score_filtered(ytrue_example, guided_lda_doc_labels, exclude_labels_from_majority=[-1], exclude_labels_from_purity=[])
top2vec_purity = purity_score_filtered(ytrue_example, predicted_labels, exclude_labels_from_majority=[-1], exclude_labels_from_purity=[])

print(f"Purity Score for nmf: {nmf_purity:.4f}")
print(f"Purity Score for lda: {lda_purity:.4f}")
print(f"Purity Score for corex: {cor_purity:.4f}")
print(f"Purity Score for our model: {own_purity:.4f}")
print(f"Purity Score for guided_lda: {guided_lda_purity:.4f}")
print(f"Purity Score for top2vec: {top2vec_purity:.4f}")
print("\n")



#NMI Scores
nmf_nmi = normalized_mutual_info_score(true_labels, nmf_doc_labels)
lda_nmi = normalized_mutual_info_score(true_labels, lda_doc_labels)
cor_nmi = normalized_mutual_info_score(true_labels, cor_doc_labels)
own_nmi = normalized_mutual_info_score(true_labels, own_doc_labels)
guided_lda_nmi = normalized_mutual_info_score(true_labels, guided_lda_doc_labels)
top2vec_nmi_score = normalized_mutual_info_score(true_labels, predicted_labels)

print(f"NMF NMI Score: {nmf_nmi:.4f}")
print(f"LDA NMI Score: {lda_nmi:.4f}")
print(f"COREX NMI Score: {cor_nmi:.4f}")
print(f"Own Model NMI Score: {own_nmi:.4f}")
print(f"GUIDED_LDA NMI Score: {guided_lda_nmi:.4f}")
print(f"Top2Vec NMI Score: {top2vec_nmi_score:.4f}")



