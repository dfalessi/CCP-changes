import jensenshannon
import numpy
#import pprint
import preprocess
reload(preprocess)
#import re
import sys
#import vectorspace
#from collections import defaultdict
from gensim import corpora, models, matutils, similarities

#from pprint import pprint
#from preprocess import Preprocessor
#from vectorspace import Corpus
#reload(vectorspace)

def main(argv):
    string1 = "herp $#!@ []  :-P derp, camelCase, CamelCase lololol ponies"
    string2 = "lalala, (sh!ny ponies :-P), sh!ny ponies"
    string3 = "Cross validated answers... are good."
    string4 = "Simply, validated answers are nice!"
    
    # TESTS
    
    #test(string1, string2)
    #test(string3, string4)
    testFile("shortPhrases.java", "I like food")

def test(string1, string2):
    pp = preprocess.Preprocessor()
    texts = [pp.preprocess(string1), pp.preprocess(string2)]
    
    #print dictionary.token2id
    getProbDists(texts)

def testFile(fileName, query):
    pp = preprocess.Preprocessor()
    fileText = pp.prepDoc(fileName, combine = True)
    #print fileText
    queryText = pp.preprocess(query)
    texts = [queryText, fileText]
    #print texts
    probDists = getProbDists(texts)
    #print probDists
    print jensenshannon.jensen_shannon_divergence(numpy.array(probDists))

def getProbDists(texts):
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    dict_size = len(dictionary.token2id)
    dists = []
    for vector in corpus:
        dists.append(probDist(dictionary, dict_size, vector))
    return dists

def probDist(dictionary, dict_size, vector):
    #print vector
    total = float(sum(x[1] for x in vector))
    #print total
    #print dictionary.values()
    probs = [0] * dict_size
    #print len(probs)
    for item in vector:
        #index = item[0]
        #freq = item[1]
        probs[item[0]] = item[1] / total
    #print probs
    return probs

# =========================
if __name__ == '__main__':
    main(sys.argv)