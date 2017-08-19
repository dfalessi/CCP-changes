# -*- coding: utf-8 -*-
'''
This implementation is from a vector space tutorial from
Radim Řehůřek's Gensim library, which requires both the SciPy
and NumPy libraries. All of these are open source software.

The Gensim, SciPy, and NumPy libraries are required for this
program.

For download and more information on Gensim, see this link:
< https://radimrehurek.com/gensim/index.html >

For download and more information on SciPy & NumPy, see this link:
< https://www.scipy.org/index.html >
'''

import numpy
import re
from collections import defaultdict
from gensim import corpora, models, similarities

class Corpus:
    
    '''
    Constructor.
    Initializes object with list of statements, preprocessed, in array form (docs).
    '''
    def __init__(self, docs):
        self.corpus = None
        self.dictionary = None
        self.index = None
        self.texts = docs
    
    '''
    createCorpus(self)
    Creates a corpus ("bag of words") with a generated dictionary.
    '''
    def createCorpus(self):
        self.dictionary = corpora.Dictionary(self.texts)
        self.corpus = [self.dictionary.doc2bow(text) for text in self.texts]
    
    '''
    calc_tfidf(self)
    Returns a list with the highest TF-IDF score of each document as compared to
    the other documents.
    '''
    def calc_tfidf(self):
        tfidf = models.TfidfModel(self.corpus)
        dict_size = len(self.dictionary.token2id)
        index = similarities.SparseMatrixSimilarity(tfidf[self.corpus], num_terms = dict_size)
        highest_scores = []
        # modified this part so it iterates over all statements
        for i in range(len(self.corpus)):
            highest = 0
            sims = index[tfidf[self.corpus[i]]]
            for j in range(0, len(self.corpus)):
                if (j != i):
                    highest = self.compare(sims[j], highest)
            highest_scores.append(numpy.float(highest))
        return highest_scores
    
    '''
    compare(self, sim, highest)
    Returns the higher score between the current score (sim) and
    highest score so far (highest).
    '''
    def compare(self, sim, highest):
        if sim > highest:
            return sim
        else:
            return highest