import re

from preprocess import Preprocessor

string = "herp $#!@ []  : )< derp, camelCase, 123MORECamelCase lololol ^&h("
#print(string.split())

p = Preprocessor()

#print(p.stripSpecialChars(string))
print p.preprocess(string)

'''
regex = '[^0-9a-zA-Z]'

newString = re.sub(regex, " ", string)
print(newString)

newStringSplit = newString.split()
print(newStringSplit)
'''