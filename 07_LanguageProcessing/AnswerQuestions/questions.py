import nltk
import sys
import os
from nltk.tokenize import word_tokenize
import string
import re
import math as m

nltk.download('stopwords')

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    dict = {}
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            print(os.path.join("/mydir", file))
            reader = open(os.path.join(directory, file), encoding="utf8")
            content = reader.read()
            dict[file] =  content
            reader.close()
    return dict
    



def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """  
    result = []
    tokens = word_tokenize(document)

    stopwords = nltk.corpus.stopwords.words("english")
    for word in tokens:
        if not word in stopwords:
            word = re.sub('[' + string.punctuation + ']', '', word)
            if not word.isspace() and not word == '':
                result.append(word.lower())
    return result    
    


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    word_to_document = {}
    for filename in documents:
        for word in documents[filename]:
            if not word in word_to_document :
                word_to_document[word] = []
            if not filename in word_to_document[word]:
                word_to_document[word].append(filename)
    result = {}
    for word in word_to_document:
        result[word] = m.log(len(documents) / len(word_to_document[word]))
    return result


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    file_idfs = {}
    for filename in files:
        file_idfs[filename] = 0
        for word in files[filename]:
            if word in query:
                file_idfs[filename] += idfs[word]

    result = []
    for count in range(n):
        biggest_probability = 0
        file_biggest_probability = ''
        for filename in file_idfs:
            if file_idfs[filename] > biggest_probability:
                file_biggest_probability = filename
                biggest_probability = file_idfs[filename]
        result.append(file_biggest_probability)
        file_idfs.pop(file_biggest_probability)
    
    return result

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_idfs = {}
    for sentence in sentences:
        sentence_idfs[sentence] = 0
        words_alread_found =[]
        for word in sentences[sentence]:
            if word in query and not word in words_alread_found:
                sentence_idfs[sentence] += idfs[word]
                words_alread_found.append(word)
    
    result = []
    for count in range(n):
        biggest_probability = -1
        sentence_biggest_probability = ''
        for sentence in sentence_idfs:
            if (sentence_idfs[sentence] == biggest_probability and check_new_has_higher_density(query, sentence_biggest_probability, sentence) or 
                sentence_idfs[sentence] > biggest_probability): #found higher idf value for a sentence
                    sentence_biggest_probability = sentence
                    biggest_probability = sentence_idfs[sentence]
            
        result.append(sentence_biggest_probability)
        sentence_idfs.pop(sentence_biggest_probability)
    return result
    
def check_new_has_higher_density(query, sentence_old_biggest_probability, new_sentence):
    #calculate density
    counter_old_sentence = 0
    counter_new_sentence = 0
    for word in query:
        if word in sentence_old_biggest_probability:
            counter_old_sentence += 1
        if word in new_sentence:
            counter_new_sentence +=1
    density_old = counter_old_sentence / len(query)
    density_new = counter_new_sentence / len(query)
    
    return True if density_new > density_old else False

if __name__ == "__main__":
    main()
