import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> N V | N V Adv
N -> NP 
NP -> Det N | P N | Adv N | Det Adj N  
V -> VP | V VP
VP -> N V | Conj VP | Adv V | V N
Adj -> Adj Adj
Det -> Det Adj
Adv -> AdvP
AdvP -> NP Adv | Conj N VP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    nltk.download('punkt')
    splitted_sentence = nltk.word_tokenize(sentence)
    result = []
    for word in splitted_sentence:
        if any(c.isalpha() for c in word):
            result.append(str.lower(word))

    return result


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    result = []
    for s in tree:
        if not isinstance(s, nltk.Tree):
            return result
        else:
            #print("Subtree:")
            #s.pretty_print()
            all_phrases = np_chunk(s)
            if len(all_phrases) == 0:
                if s._label == 'NP':
                    result.append(s)
            else:
                for np in all_phrases:
                    result.append(np)
    return result


if __name__ == "__main__":
    main()
