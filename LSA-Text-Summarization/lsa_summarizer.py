from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
import math
import numpy
import math
from warnings import warn
from nltk.tokenize import sent_tokenize, word_tokenize
from numpy.linalg import svd as singular_value_decomposition
from base_summarizer import BaseSummarizer
from nltk.corpus import stopwords
from xml_parser import XMLParser
from stop_words import safe_get_stop_words
from rouge import Rouge
import sys
sys.setrecursionlimit(1500)

class LsaSummarizer(BaseSummarizer):
    MIN_DIMENSIONS = 3
    REDUCTION_RATIO = 1/1

    _stop_words = list(stopwords.words('english'))

    # _stop_words = safe_get_stop_words("bulgarian")

    @property
    def stop_words(self):
        return self._stop_words

    @stop_words.setter
    def stop_words(self, words):
        self._stop_words = words

    def __call__(self, sentences_count):

        # word -> row index (document is given in one row)
        dictionary = self._create_dictionary()
        
        if not dictionary:
            return ()

        sentences = self.load_sentences()


        matrix = self._create_matrix(dictionary)
        matrix = self._compute_term_frequency(matrix)
        u, sigma, v = singular_value_decomposition(matrix, full_matrices=False)

        # evaluating(ranking) the sentence importance
        ranks = iter(self._compute_ranks(sigma, v))

        # a = next(ranks)
        # b = next(ranks)
    

        return self._get_best_sentences(sentences, len(sentences),
            lambda s: next(ranks))

    def set_filepath(self, filePath):
        self.filePath = filePath

    def load_sentences(self):
        if self.filePath.endswith('.xml'):
            parser = XMLParser()
            data = parser.read(self.filePath)
        else:
            f = open(self.filePath, "r", encoding="utf8")
            data= f.read()

        sentences = sent_tokenize(data)
        return self.summarize(sentences,"ball",len(sentences),5)

    # dictionary[word, indexInText]
    def _create_dictionary(self):
        raw_sentences = self.load_sentences()
        words = []
        for sentence in raw_sentences:
           words.append(word_tokenize(sentence))
        flat_words = [item for sublist in words for item in sublist]
        flat_words = tuple(flat_words)

        # all the words to lower case
        flat_words = map(self.normalize_word, flat_words)

        unique_words = frozenset(w for w in flat_words if w not in self._stop_words)

        return dict((w, i) for i, w in enumerate(unique_words))

    # creating matrix containing info about words(rows) occurences in sentences(columns)
    def _create_matrix(self, dictionary):
        sentences = self.load_sentences()
        words_count = len(dictionary)
        sentences_count = len(sentences)
        if words_count < sentences_count:
            message = (
                "Number of words (%d) is lower than number of sentences (%d). "
                "LSA algorithm may not work properly."
            )
            warn(message % (words_count, sentences_count))

        matrix = numpy.zeros((words_count, sentences_count))
        for col, sentence in enumerate(sentences):
            words = word_tokenize(sentence)
            for word in words:
                # only valid words is counted (not stop-words, ...)
                if word in dictionary:
                    row = dictionary[word]
                    matrix[row, col] += 1

        return matrix


    # Note: TF == Term Frequency
    # Computes TF metrics for each sentence (column) in the given matrix and  normalize 
    # the tf weights of all terms occurring in a document by the maximum tf in that document 
    # according to ntf_{t,d} = a + (1-a)\frac{tf_{t,d}}{tf_{max}(d)^{'}}.
    
    # The smoothing term $a$ damps the contribution of the second term - which may be viewed 
    # as a scaling down of tf by the largest tf value in $d$
    def _compute_term_frequency(self, matrix, smooth=0.4):
        
        assert 0.0 <= smooth < 1.0

        max_word_frequencies = numpy.max(matrix, axis=0)
        rows, cols = matrix.shape
        for row in range(rows):
            for col in range(cols):
                max_word_frequency = max_word_frequencies[col]
                if max_word_frequency != 0:
                    frequency = matrix[row, col]/max_word_frequency  # maybe it gets how important the word is according to the sentence
                    matrix[row, col] = smooth + (1.0 - smooth)*frequency

        return matrix

    def _compute_ranks(self, sigma, v_matrix):
        assert len(sigma) == v_matrix.shape[0]

        dimensions = max(LsaSummarizer.MIN_DIMENSIONS,
            int(len(sigma)*LsaSummarizer.REDUCTION_RATIO))
        powered_sigma = tuple(s**2 if i < dimensions else 0.0
            for i, s in enumerate(sigma))

        ranks = []

        for column_vector in v_matrix.T:
            # Enhanced LSA Summarization (the following line is mentioned in this paragraph) ?
            rank = sum(s*v**2 for s, v in zip(powered_sigma, column_vector))
            ranks.append(math.sqrt(rank))

        return ranks
    def summarize(self,sentences, keywords, sentences_count, size_of_chunks):
        similarity_for_chuns = [(-1,0.0)]
        n = 2
        for i in range(sentences_count-size_of_chunks):
           similarity = self.jaccard_similarity(''.join(sentences[i:i+size_of_chunks]),keywords)
           similarity_for_chuns = numpy.append(similarity_for_chuns, [[i,similarity]], 0)

        if len(similarity_for_chuns) < n:
            n = len(similarity_for_chuns)
        similarity_for_chuns = sorted(similarity_for_chuns, key=lambda x: x[1],reverse=True)[0:n]
        sort_by_index = sorted(similarity_for_chuns, key=lambda x: x[0],reverse=False)
        new_sentences = []
        for i in range(n):
            if i >= len(sort_by_index):
                break
            start_index = int(sort_by_index[i][0])
            for j in range(size_of_chunks):
               if not sentences[j+start_index] in new_sentences:
                  new_sentences = numpy.append(new_sentences,sentences[start_index+j])
        return new_sentences

    def jaccard_similarity(self,doc_1, doc_2):
        a = set(doc_1.split())
        b = set(doc_2.split())
        c = a.intersection(b)
        return float(len(c)) / (len(a) + len(b) - len(c)) 