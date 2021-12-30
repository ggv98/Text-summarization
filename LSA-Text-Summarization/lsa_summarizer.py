from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
import math
import numpy

from warnings import warn
from nltk.tokenize import sent_tokenize, word_tokenize
from numpy.linalg import svd as singular_value_decomposition
from base_summarizer import BaseSummarizer
from nltk.corpus import stopwords

from stop_words import safe_get_stop_words

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

    def __call__(self, document, sentences_count):

        # word -> row index (document is given in one row)
        dictionary = self._create_dictionary(document)
        
        if not dictionary:
            return ()

        sentences = sent_tokenize(document)

        matrix = self._create_matrix(document, dictionary)
        matrix = self._compute_term_frequency(matrix)
        u, sigma, v = singular_value_decomposition(matrix, full_matrices=False)

        # evaluating(ranking) the sentence importance
        ranks = iter(self._compute_ranks(sigma, v))

        # a = next(ranks)
        # b = next(ranks)

        return self._get_best_sentences(sentences, sentences_count,
            lambda s: next(ranks))

    # dictionary[word, indexInText]
    def _create_dictionary(self, document):
        words = word_tokenize(document)
        words = tuple(words)

        # all the words to lower case
        words = map(self.normalize_word, words)

        unique_words = frozenset(w for w in words if w not in self._stop_words)

        return dict((w, i) for i, w in enumerate(unique_words))

    # creating matrix containing info about words(rows) occurences in sentences(columns)
    def _create_matrix(self, document, dictionary):
        sentences = sent_tokenize(document)
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