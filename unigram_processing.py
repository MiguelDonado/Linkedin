# Script that will process the descriptions of the jobs offered by some of the most
# important companies in the IT sector
# The name of those companies will be stored in a list, on 'constants.py'

# This script basically process the descriptions of the jobs that have been saved on a .txt
# Particularly to process the data (sequences of text), first we have to tokenize it,
# in order to tokenize it we can consider words as tokens (unigrams), that's what we are gonna apply on this script
# When tokenizing a sequence of text, we could also consider characters as tokens or n-grams as tokens.
# All this info about the jobs has been scraped and saved on the file by another script

import sys

import regex
import spacy

# Load English model
nlp = spacy.load("en_core_web_sm")

words = {}
job_words = count_words(clean_description_job)
words = sum_dicts(words, job_words)
noun_counts = {word: count for word, count in words.items() if Linkedin.is_noun(word)}
noun_counts = dict(sorted(noun_counts.items(), key=lambda item: item[1], reverse=True))
with open("Linkedin.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    writer.writerow(["word", "count"])

    for word, count in noun_counts.items():
        writer.writerow([word, count])


# In order to count the words, I saw I could have used regex to split the words into a list,
# And collection.Counter to count the words in the list
# But I felt like doing it from scratch, just to play a little bit with the logic (loops, conditionals...)
def count_words(text):
    # 1. Split the text into words
    allowed_symbols = ["_", "-", "+", "/"]
    # List that will hold all words
    words = []
    # Variable that will hold a word
    word = ""
    for char in text:
        if char.isalnum() or char in allowed_symbols:
            word += char.lower()
        else:
            if word != "":
                words.append(word)
                word = ""
    # 2. Handle last word
    if word != "":
        words.append(word)

    # Count ocurrences
    word_count = {}
    for w in words:
        if w in word_count:
            word_count[w] += 1
        else:
            word_count[w] = 1
    return word_count


def sum_dicts(d1, d2):
    result = {}

    # Add all items from d1
    for key in d1:
        result[key] = d1[key]

    # Add items from d2
    for key in d2:
        if key in result:
            result[key] += d2[key]
        else:
            result[key] = d2[key]

    return result


# Check if a word is a noun
def is_noun(word):
    doc = nlp(word)
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN"):
            return True
        return False
