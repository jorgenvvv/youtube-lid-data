#!/usr/bin/env python3

import argparse
import heapq
import json
import logging
import os
import random
import sys

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from polyglot.detect import Detector
from tqdm import tqdm


def read_random_documents(file_name: str, documents_count: int) -> list:
    logging.info(f'Selecting {documents_count} random documents')

    with open(file_name, encoding='utf-8') as fin:
        documents_json = heapq.nlargest(
            documents_count, fin, key=lambda L: random.random())

    documents = []

    pbar = tqdm(documents_json)
    pbar.set_description('Processing random documents')
    for d in pbar:
        document = json.loads(d)
        documents.append(document['title'] + '\n' + document['text'])

    return documents

def calculate_ngrams(documents: list, document_top_phrases: int, phrase_length: int) -> list:
    logging.info(f'Generating search phrases')

    tfidf_vectorizer = TfidfVectorizer(
        ngram_range=(phrase_length, phrase_length),
        use_idf=True
    )
    tfidf_vectorizer_vectors = tfidf_vectorizer.fit_transform(documents)

    feature_names = np.array(tfidf_vectorizer.get_feature_names())

    # ngrams = feature_names[tfidf_vectorizer_vectors.argmax(axis=1)]

    # Take top n ngrams per document
    ngrams = feature_names[
            np.argsort(-tfidf_vectorizer_vectors.toarray(), axis=1)[
                :, :document_top_phrases
            ]
    ].flatten().tolist()

    return ngrams

def is_phrase_valid(phrase: str, language: str) -> bool:
    phrase_words = phrase.split()
    
    # No duplicate words in phrase
    if len(phrase_words) != len(set(phrase_words)):
        return False

    # Word cannot be just numbers
    for w in phrase_words:
        if w.isdigit():
            return False

    # Check language
    detector = Detector(phrase, quiet=True)
    if detector.language.code != language:
        return False

    return True

def filter_phrases(phrases: list, language: str) -> None:
    logging.info('Filtering generated phrases')

    valid_phrases = []

    for phrase in phrases:
        if is_phrase_valid(phrase, language):
            valid_phrases.append(phrase)

    return valid_phrases


def write_output_phrases(file_name: str, ngrams: list, output_path: str) -> None:
    os.makedirs(output_path, exist_ok=True)
    language_code = os.path.basename(file_name).split('_')[0]
    output_file_name = language_code + '_search_phrases.txt'
    output_path_name = os.path.join(output_path, output_file_name)
    
    logging.info(f'Writing output to {output_path_name}')

    os.makedirs(os.path.dirname(output_path_name), exist_ok=True)

    with open(output_path_name, 'w') as fout:
        for ngram in ngrams:
            fout.write(f'{ngram}\n')


def generate_phrases(file_name: str, document_limit: int, document_top_phrases: int, output_path: str, phrase_length: int) -> None:
    documents = read_random_documents(file_name, document_limit)
    
    ngrams = calculate_ngrams(documents, document_top_phrases, phrase_length)
    
    language_code = os.path.basename(file_name).split('_')[0]
    valid_phrases = filter_phrases(ngrams, language_code)
    
    write_output_phrases(file_name, valid_phrases, output_path)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    parser = argparse.ArgumentParser(
        description='Generate search phrases from Wikipedia documents by applying TF-IDF on the data and finding top n ngrams for each document.'
    )

    parser.add_argument('-i', '--input', type=str,
                        help='path to an input file or a directory')
    parser.add_argument('-o', '--output-path', type=str, default='./',
                        help='path to a directory where to write the output file(s)')
    parser.add_argument('--phrase-length', type=int, default=3, metavar='N',
                        help='length of search phrase (amount of words)')
    parser.add_argument('--document-limit', type=int, default=2500, metavar='N',
                        help='maximum amount how many random documents to use')
    parser.add_argument('--document-top-phrases', type=int, default=10, metavar='N',
                        help='how many top phrases to take from one document')

    args = parser.parse_args()

    if not len(sys.argv) > 1:
        parser.print_help()
        parser.exit()

    if args.input:
        if os.path.isfile(args.input):
            logging.info(
                f'Generating search phrases for file {os.path.basename(args.input)}')
            generate_phrases(args.input, args.document_limit,
                             args.document_top_phrases, args.output_path, args.phrase_length)

        elif os.path.isdir(args.input):
            if not os.listdir(args.input):
                print('Provided input directory does not contain any files')
                parser.exit()
            
            logging.info(
                f'Generating search phrases for files in directory {args.input}')

            for file in os.listdir(args.input):
                current_file = os.path.join(args.input, file)
                if os.path.isfile(current_file):
                    generate_phrases(
                        current_file, args.document_limit, args.document_top_phrases, args.output_path, args.phrase_length)

        else:
            print('Invalid input file or directory')
            parser.exit()
