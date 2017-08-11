import re

from preprocess import Preprocessor

string = "herp $#!@ []  : )< derp, camelCase, 123MORECamelCase lololol ^&h("
#print(string.split())

p = Preprocessor()

#print(p.stripSpecialChars(string))
print p.preprocess(string)

string2 = "verbs: running, ran, walked, seen, seeing, hopping, swam, $#!+ment, (golfing). adjectives: red, or@nge, dus-ty, (sh!ny:-P)"
print p.preprocess(string2)

string3 = "caressed, ponies, oxen, boxes, geese, goose, velvet, varieties, deities, fish, people, humans, soybeans, shivers"
print p.preprocess(string3)