import os
import sys
import numpy as np
import pandas as pd
import networkx as nx
import multiprocessing
from nltk.tokenize import sent_tokenize
from stop_words import safe_get_stop_words
from gensim.models import Word2Vec
from scipy import spatial
from rouge import Rouge
from pathlib import Path
sys.path.append('parsers')
from xml_parser import XMLParser

class TextRankSummarizator():
    def __init__(self, language):
        self.stop_words = safe_get_stop_words(language)
        # self.w2v_model = {}
        
        # Use pretrained model for english
        # self.load_pretrained_word2vec_model()

    def set_filepath(self, filePath):
        self.filePath = filePath

    def load_pretrained_word2vec_model(self):
        f = open('./glove/glove.6B.100d.txt', encoding='utf-8')
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            self.w2v_model[word] = coefs
        f.close()

    def load_sentences(self):
        if str(self.filePath).endswith('.xml'):
            parser = XMLParser()
            data = parser.read(self.filePath)
        else:
            f = open(self.filePath, "r", encoding="utf8")
            data= f.read()

        sentences = sent_tokenize(data)
        return sentences

    def sentence_normalization(self, sentences):
        # remove punctuations
        clean_sentences = pd.Series(sentences).str.replace("[^a-zA-Zа-яА-Я]", " ")

        # remove uppercase
        clean_sentences = [s.lower() for s in clean_sentences]

        #remove stopwords
        clean_sentences = [self.remove_stopwords(r.split()) for r in clean_sentences]

        return clean_sentences

    def remove_stopwords(self, sentence):
        newSentence = " ".join([i for i in sentence if i not in self.stop_words])
        return newSentence

    def sentence_embeddings(self, sentences):
        # Extract word vectors
        cores = multiprocessing.cpu_count()
        w2v_model = Word2Vec(vector_size=10,
                            min_count=1,
                            workers=cores-1)
        w2v_model.build_vocab(sentences)

        total_examples = w2v_model.corpus_count
        w2v_model.train(sentences, total_examples=total_examples, epochs=w2v_model.epochs)
        sentence_embeddings=[[sum(w2v_model.wv[word]) for word in words] for words in sentences]
        max_len=max([len(tokens) for tokens in sentences])
        sentence_embeddings=[np.pad(embedding,(0,max_len-len(embedding)),'constant') for embedding in sentence_embeddings]
        
        return sentence_embeddings

    def build_similarity_matrix(self, normalized_sentences, sentence_embeddings):
        similarity_matrix = np.zeros([len(normalized_sentences), len(normalized_sentences)])
        for i,row_embedding in enumerate(sentence_embeddings):
            for j,column_embedding in enumerate(sentence_embeddings):
                if similarity_matrix[i][j] == 0:
                    similarity_matrix[j][i] = similarity_matrix[i][j] = 1 - spatial.distance.cosine(row_embedding,column_embedding)
        similarity_matrix[np.isnan(similarity_matrix)] = 0
        return similarity_matrix

    def rank_sentences(self, similarity_matrix, raw_sentences):
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank_numpy(nx_graph)

        ranked_sentences = sorted(((scores[i],s, i) for i,s in enumerate(raw_sentences)), reverse=True)

        return ranked_sentences

    def construct_summary(self, ranked_sentences, number_of_sentences):
        selected_sentences = ranked_sentences[:number_of_sentences]
        selected_sentences.sort(key=lambda a: a[2])
        summary = ''
        for s in selected_sentences:
            summary += s[1] + '\n'#(str(s[0]) + ' -> ' + str(s[2]) + '\n')
        
        return summary        

    #"tennis.csv"
    #"cloud_tech.txt"
    def get_summary(self, len):
        raw_sentences = self.load_sentences()
        normalized_sentences = self.sentence_normalization(raw_sentences)
        sentence_embeddings = self.sentence_embeddings(normalized_sentences)
        similarity_matrix = self.build_similarity_matrix(normalized_sentences, sentence_embeddings)
        ranked_sentences = self.rank_sentences(similarity_matrix, raw_sentences)
        summary = self.construct_summary(ranked_sentences, len)

        return summary




def evaluate():
    original_summaries = []
    generated_summaries = []
    summarizator = TextRankSummarizator('english') 
    cwd = Path.cwd()
    main_dir = Path.joinpath(cwd, 'top1000-complete')
    for index, filename in enumerate(os.listdir(main_dir)):
        if index == 50: break
        print(index, filename)
        summarizator.set_filepath(Path.joinpath(main_dir, filename, 'Documents_xml', filename + '.xml'))
        f = open(Path.joinpath(main_dir, filename, 'summary', filename + '.gold.txt'), "r", encoding="utf8")
        # try:
        original_summaries.append(f.read())
        summary = summarizator.get_summary(original_summaries[-1].count('\n')+5)

        generated_summaries.append(summary)


    rouge = Rouge()
    print(rouge.get_scores(original_summaries, generated_summaries, avg=True))
    print('\n')

evaluate()

def evaluate_bg():
    original_summaries = []
    generated_summaries = []
    summarizator = TextRankSummarizator('bulgarian') 
    cwd = Path.cwd()
    main_dir = Path.joinpath(cwd, 'bg_articles')
    for index, filename in enumerate(os.listdir(main_dir)):
        if index == 50: break
        print(index, filename)
        summarizator.set_filepath(Path.joinpath(main_dir, filename, 'text.txt'))
        f = open(Path.joinpath(main_dir, filename, 'summary.txt'), "r", encoding="utf8")
        # try:
        original_summaries.append(f.read())
        summary = summarizator.get_summary(original_summaries[-1].count('\n')+5)

        generated_summaries.append(summary)


    rouge = Rouge()
    print(rouge.get_scores(original_summaries, generated_summaries, avg=True))
    print('\n')

# evaluate_bg()


