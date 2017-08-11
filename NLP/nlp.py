import sys
from preprocess import Preprocessor

def main(argv):
    if len(argv) < 2:
        print "Invalid arguments. Format is \'python nlp.py [file name]\'"
    else:
        pp = Preprocessor()
        print "Starting NLP..."
        with open(argv[1]) as file:
            for line in file:
                # Stubbed out for now
                print pp.preprocess(line)

if __name__ == '__main__':
    main(sys.argv)