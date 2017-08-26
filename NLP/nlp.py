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

import sys
from gensim import *

from preprocess import Preprocessor
from vectorspace import Corpus

'''
main.
'''
def main(argv):
    if len(argv) < 2:
        print "Invalid arguments. Format is \'python nlp.py [file name]\'"
    else:
        pp = Preprocessor()
        print "Starting NLP..."
        texts = pp.prepDoc(argv[1])
        c = Corpus(texts)
        c.createCorpus()
        scores = c.calc_tfidf()
        export(scores)

'''
export(scores)
Exports the list of scores with their corresponding document numbers
to a csv file.
'''
def export(scores):
    with open('vector_space_scores.csv','wb') as file:
        file.write("doc #,high_score\n")
        for i in range(0, len(scores)):
            file.write("%3d,%f\n" % (i, scores[i]))
    print("Exported to \'vector_space_scores.csv\'.")

'''
printScores(scores)
Prints the list of scores with their corresponding document numbers.
For testing/debugging purposes only.
'''
def printScores(scores):
    print type(scores[0])
    print "-- HIGHEST SCORES --\n"
    for i in range (0, len(scores)):
        print("Statement #%d: %f" % (i, scores[i]))

# =========================
if __name__ == '__main__':
    main(sys.argv)