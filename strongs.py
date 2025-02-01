import json
# from nltk.corpus import stopword
from random import choice, sample
import re
# from nltk.tokenize import word_tokenize
# import nltk
 
#  *
#  *                 A Concise Dictionary of the Words 
#  *                       in the Hebrew Bible
#  *                   with their Renderings in the 
#  *                        King James Version
#  *                                by 
#  *                    James Strong, LL.D., S.T.D.
#  *                               1894
#  *
#  * JSON version
#  * ============
#  * Copyright 2010, Open Scriptures. CC-BY-SA. Derived from XML.
#  * $Id$
#  *
#  * XML e-text version
#  * ==================
#  * From a source by David Instone-Brewer (www.2LetterLookup.com):
#  * "The data came from several PD sources which were full of errors. 
#  * I cleaned them by comparing them to each other and (where 
#  * necessary) looking at the original."
#  *
#  * Editing, corrections and Unicode transliterations
#  * by David Troidl.
#  *
#  * Comments or corrections:
#  * open-scriptures@googlegroups.com
#  *
#  *                      Dictionary of Greek Words
#  *                              taken from
#  *                    Strong's Exhaustive Concordance
#  *                                   by
#  *                      James Strong, S.T.D., LL.D.
#  *                                  1890
#  * 
#  * JSON version
#  * ============
#  * Copyright 2009, Open Scriptures. CC-BY-SA. Derived from XML.
#  * $Id$
#  *
#  * XML e-text version
#  * ==================
#  * 
#  * The XML version of this work was prepared in 2006 by Ulrik Petersen
#  * (http://ulrikp.org) from the ASCII e-text version presented below.
#  * The XML version contains "real" UTF-8 Greek where the original ASCII
#  * e-text version had transliteration.  The XML has a stand-alone DTD
#  * which should be easy to follow.
#  * 
#  * Ulrik Petersen welcomes bugfixes to the text.  Please send them to the
#  * address provided on the website:
#  * 
#  * http://ulrikp.org
#  * 
#  * Ulrik Petersen
#  *

# nltk.download('punkt_tab')
STOPWORDS_ENGLISH = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 
'ourselves', 'you', 'thou', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 
'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 
'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 
'with', 'about', 'into', 'through', 'to', 'from', 'in', 'out', 'on', 'off', 'again', 'then', 'once', 
'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 
'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 
's', 't', 'can', 'will', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y',
 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 
'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn',
 "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 
'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't",
"and", "also", "both", "but", "even", "for", "if", "or", "so", "that", "then", "therefore", "when", "yet",
"have", "hold", "as", "like", "when", "while", "since", "become", "some", "etc", "cause", "do", "happen", "have",
"again", "alike", "also", "but", "either", "even", "for", "all", "likewise", "moreover", "nay", "neither", "though", "yea"]
EXTRA_STOPS = ['against', 'between', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'over', 'under', 'further',]
STOP_LINGUISTICS = ['preposition', 'article', 'conjunction', "prep", "conj", "inrg", "pronoun"]
class StrongsDict():
    def __init__(self):
        self.strongs_path = r"strongs-dictionary.json"
        self.dictionary = self._read_dict()
    
    def get_dict(self):
        return self.dictionary
    
    def get_random_entry(self, k=5):
        return [f"{x}" for x in sample(sorted(dictionary.get_dict().items()), k)]
    
    def get_random_ids(self, k=5):
        return [f"{x[0]}" for x in sample(sorted(dictionary.get_dict().items()), k)]

    def get_data(self, id):
         """Get all the data for a given strongs number"""
         return self.dictionary[id]
    
    def get_definition(self, id):
        return self.dictionary[id]['strongs_def']
    
    def get_words(self, id):
        return self.dictionary[id]['kjv_def']
    
    def get_type(self, id):
        return self.dictionary[id]['derivation']
    
    def get_lemma(self, id):
        return self.dictionary[id]['lemma']
    
    def get_translit(self, id):
        return self.dictionary[id]['translit']
    
    def get_derivation(self, id):
        return self.dictionary[id]['derivation']

    def _read_dict(self):
        """Reads json and returns strongs dictionary in the form "strong_number": {info}"""
        with open(self.strongs_path, 'r', encoding='utf-8') as config_file:
            data_loaded = json.load(config_file)
        
        return data_loaded
    
    def is_stopword(self, id):
        """Checks whether a strong value is a (probable) stop word.""" 
        words = self.get_words(id).replace(" ", "`").replace("...", ",")
        words = re.sub(r"\(.+?\)", '', words) # replace any "( ... )", as this extra information will confuse the stop-checker
        words = re.sub(r"\[.+?\]", '', words) # replace any "[ ... ]"
        stop_words = set(STOPWORDS_ENGLISH)
        word_tokens = word_tokenize(words)
        word_tokens = "".join(word_tokens).replace("`", " ").split(",")

        ## TODO 
        ## Need to tokenize -> rejoin, replace, split, REMOVE token words from SPLITS (!! implement) and then check for stop words
        ## Is currently not checking for words

        list_of_stops = [w for w in word_tokens if w.lower().strip() in stop_words]

        if [i for i in STOP_LINGUISTICS if i in self.get_derivation(id)]:
            # If word is a preposition, article, etc (as defined in the dataset)
            return True
        elif len(words) == 0 :
            # If word is undefined
            return True
        elif len(list_of_stops) >= len(words.split(",")) / 2 :
            # If over half of translations are stop words, is probably stop word
            return True
                
        return False

            
if __name__ == "__main__":#
    dictionary = StrongsDict()
    ids = "G3004"
    id2 = "G2532"
    id3 = "G191"
    id4 = "H638"
    id5 = "G2192"
    id6 = "H9009"
    id7 = "H4480"
    id8 = "H1571"
    list_of_ids = [ids, id2, id3, id4, id5, id6, id7, id8]
    # list_of_ids = dictionary.get_random_ids(30)
    for id in list_of_ids:
        print(f"==== {id} ====")
        print(dictionary.get_data(id))
        # print(dictionary.get_definition(id))
        print(dictionary.get_words(id))
        # print(dictionary.get_type(id))
        # print(dictionary.get_lemma(id))
        print(dictionary.get_translit(id))
        print(dictionary.is_stopword(id))

