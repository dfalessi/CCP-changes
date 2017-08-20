# -*- coding: utf-8 -*-
'''
This implementation is from a vector space tutorial from
Radim Řehůřek's Gensim library, which requires both the SciPy
and NumPy libraries. All of these are open source software.

The Gensim, SciPy, and NumPy libraries are required for this
program.

This implementation also requires Vivek Kulkarni's Jensen-Shannon
Divergence calculator (imported in jensenshannon.py).

For download and more information on Gensim, see this link:
< https://radimrehurek.com/gensim/index.html >

For download and more information on SciPy & NumPy, see this link:
< https://www.scipy.org/index.html >

For download and more information on Vivek Kulkarni's JSD calculator,
see this link:
< https://github.com/viveksck/langchangetrack/ >
'''

import sys
from gensim import corpora, models, matutils, similarities
import numpy
import jensenshannon
import preprocess

'''
main.
'''
def main(argv):
    if len(argv) < 3:
        print "Invalid arguments." \
        + " Format is \'python jsd.py [file name] \' \"query\" \'"
    else:
        div = jsd(argv[1], argv[2])
        export(div[0])

'''
testFile(fileName, query)
Returns the Jensen-Shannon Divergence score of the file and query.
'''
def jsd(fileName, query):
    pp = preprocess.Preprocessor()
    fileText = pp.prepDoc(fileName, combine = True)
    queryText = pp.preprocess(query)
    texts = [queryText, fileText]
    probDists = getProbDists(texts)
    return jensenshannon.jensen_shannon_divergence(numpy.array(probDists))

'''
probDist(dictionary, dict_size, vector)
Returns the probability distribution of the specified vector based on the
given dictionary and dictionary size.
'''
def probDist(dictionary, dict_size, vector):
    total = float(sum(x[1] for x in vector))
    probs = [0] * dict_size
    for item in vector:
        #item[0] = index, item[1] = frequency of token
        probs[item[0]] = item[1] / total
    return probs

'''
getProbDists(texts)
Builds and returns the probability distributions of a list of vectors (texts)
based on the provided dictionary.
'''
def getProbDists(texts):
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    dict_size = len(dictionary.token2id)
    dists = []
    for vector in corpus:
        dists.append(probDist(dictionary, dict_size, vector))
    return dists

'''
export(score)
Exports the score to a csv file.
'''
def export(score):
    print float(score)
    #print type(score)
    with open('jsd.csv','wb') as file:
        file.write("JSD score,%f\n" % (float(score)))
    print("Exported to \'jsd.csv\'.")
        

# =========================
if __name__ == '__main__':
    main(sys.argv)