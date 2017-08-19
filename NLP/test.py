import re
import pprint
import preprocess
import vectorspace

#from pprint import pprint
#from preprocess import Preprocessor
#from vectorspace import Corpus
reload(vectorspace)

p = preprocess.Preprocessor()

string1 = "herp $#!@ []  : )< derp, camelCase, 123MORECamelCase lololol ^&h( ponies"
#print p.preprocess(string1)

string2 = "verbs: running, ran, walked, seen, seeing, hopping, swam, $#!+ment, (golfing). adjectives: red, or@nge, dus-ty, (sh!ny:-P)"
#print p.preprocess(string2)

string3 = "caressed, ponies, oxen, boxes, geese, goose, velvet, varieties, deities, fish, people, humans, soybeans, shivers, sh!ny"
#print p.preprocess(string3)

string4 = "meh meep nah this is a test string, blah blah blah"
#print p.preprocess(string4)

texts = [p.preprocess(string1), p.preprocess(string2), p.preprocess(string3), p.preprocess(string4)]
#pprint(texts)

c = vectorspace.Corpus(texts)
c.createCorpus()
print c.calc_tfidf()