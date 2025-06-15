# Script that will process the descriptions of the jobs offered by some of the most
# important companies in the IT sector
# The name of those companies will be stored in a list, on 'constants.py'

# This script basically process the descriptions of the jobs that have been saved on a .txt
# Particularly to process the data (sequences of text), first we have to tokenize it,
# in order to tokenize it we can consider n-grams, particularly (bigrams), that's what we are gonna apply on this script
# When tokenizing a sequence of text, we could also consider characters as tokens or n-grams as tokens.
# All this info about the jobs has been scraped and saved on the file by another script

import csv
import sys

import regex
import spacy

# Load English model
nlp = spacy.load("en_core_web_sm")


def main():
    # Load txt data
    bigrams = {}

    # Load jobs line by line and update dictionary at fly
    with open("description_jobs.txt", "r") as file:
        for line in file:
            words = find_words(line)

            for i in range(len(words) - 1):
                pair = (words[i], words[i + 1])
                if pair in bigrams:
                    bigrams[pair] += 1
                else:
                    bigrams[pair] = 1
        bigrams_sorted = dict(
            sorted(bigrams.items(), key=lambda item: item[1], reverse=True)
        )

    # Write into csv the word count
    with open("Linkedin_bigrams.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(["word", "count"])

        for word, count in bigrams_sorted.items():
            writer.writerow([word, count])


# In order to count the words, I saw I could have used regex to split the words into a list,
# And collection.Counter to count the words in the list
# But I felt like doing it from scratch, just to play a little bit with the logic (loops, conditionals...)
def find_words(text):
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
    return words


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


if __name__ == "__main__":
    main()
