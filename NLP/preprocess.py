import re

class Preprocessor:
    
    '''
    Constructor. Initializes object with pre-compiled regexes.
    '''
    def __init__(self):
    
        self.spec_chars_regex = re.compile('[^0-9a-zA-Z]')
        self.camel_case_regex_1 = re.compile('(.)([A-Z][a-z]+)')
        self.camel_case_regex_2 = re.compile('([a-z0-9])([A-Z])')
    
    '''
    removeSpecialChars(self, string)
    Returns a copy of string with all non-alphanumeric characters replaced by whitespace.
    '''
    def removeSpecialChars(self, string):
        return self.spec_chars_regex.sub(' ', string)
    
    '''
    splitCamelCase(self, string)
    Returns a copy of string with each camelCase word split into separate words with whitespace in between.
    '''
    def splitCamelCase(self, string):
        newString = self.camel_case_regex_1.sub(r'\1 \2', string)
        return self.camel_case_regex_2.sub(r'\1 \2', newString)
    
    '''
    preprocess(self, string)
    Replaces all special (non-alphanumeric) characters in string with whitespace,
        splits all camelCase words in string into separate words with whitespace in between,
        and returns a list of all words (in lowercase) found in the edited string.
    '''
    def preprocess(self, string):
        newString = self.removeSpecialChars(string)
        newString = self.splitCamelCase(newString)
        return newString.lower().split()