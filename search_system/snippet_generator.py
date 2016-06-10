from copy import copy

from pymorphy2 import MorphAnalyzer

from search_engine.db.cassandra_manager import CassandraManager
from search_engine.utils import word_tokenize_save_separators


class SnippentsGenerator:
    def __init__(self, length):
        self.__cassandra_conn = CassandraManager()
        self.__snippet_len = length

    def __custom_init(self, url, query):
        self.__snippet = ''
        self.__words = []
        self.__analyzer = MorphAnalyzer()
        self.__url = url
        self.__query = query
        self.__query_length = len(self.__query)

        document = self.__cassandra_conn.get_document(self.__url)

        self.__title = document.title
        self.__h1 = document.h1
        self.__sentences = document.sentences.splitlines()

    def feed(self, url, query):
        self.__custom_init(url, query)
        self.__split_and_ranking_sentences()
        self.__generate_snippet()
        self.__normalize_snippet()

    def __split_and_ranking_sentences(self):
        for index, sentence in enumerate(self.__sentences):
            rank = 1
            terms_in_sentence = 0
            positions = []
            indexes = [0] * self.__query_length
            min_dist = 9999999
            sentence_length = len(sentence)

            if sentence[-1] in '.!':
                rank *= 1.2

            words = [
                self.__analyzer.parse(word.lower())[0].normal_form
                for word in word_tokenize_save_separators(sentence)
            ]

            for term in self.__query:
                if term in words:
                    rank *= 1.1

                temp_positions = [index for index in range(len(words)) if words[index] == term]

                if temp_positions:
                    positions.append(temp_positions)

            if terms_in_sentence == self.__query_length:
                rank *= 1.3

            if 80 < sentence_length < 150:
                rank *= 1.2
            elif sentence_length > 100:
                rank *= 1.1

            last_indexes = [len(item) - 1 for item in positions]

            while True:
                passage = []

                for i, term_positions in zip(indexes, positions):
                    passage.append(term_positions[i])

                dist = sum([abs(passage[i] - passage[i - 1]) for i in range(1, len(passage))])

                if dist < min_dist and dist > 0:
                    min_dist = dist

                temp_passage = copy(passage)

                while True:
                    if not temp_passage:
                        i = None
                        break

                    _min = min(temp_passage)
                    temp_passage.remove(_min)
                    i = passage.index(_min)

                    if indexes[i] < last_indexes[i]:
                        indexes[i] += 1
                        break

                if i is None:
                    break

            rank *= 1 + (1 / min_dist)
            rank *= 1 + (1 / (1 + index))
            l = [rank, sentence_length, index, words]
            self.__words.append(l)
            self.__words.sort(reverse=True)

    def __generate_snippet(self):
        snippet_length = 0
        candidates = []
        snippet = []

        while snippet_length < (self.__snippet_len - 50):
            try:
                candidate = self.__words.pop(0)
            except IndexError:
                break

            snippet_length += candidate[1]
            candidates.append([candidate[2], candidate[3]])

        candidates.sort()
        for sentence in self.__sentences:
            sentence = word_tokenize_save_separators(sentence)

            for index, item in enumerate(sentence):
                if item.lower() in self.__query:
                    sentence[index] = ''.join(['<mark>', sentence[index], '</mark>'])

            sentence = ''.join(sentence)
            snippet.append(sentence)

        self.__snippet = ' '.join(snippet)

    def __normalize_snippet(self):
        if len(self.__snippet) > self.__snippet_len:
            index = self.__snippet_len - 1
            snippet = list(self.__snippet[:index])
            dot = False
            index -= 1

            while True:
                if snippet[index].isspace():
                    symbol_code = ord(snippet[index - 1])
                    if (1072 <= symbol_code <= 1103 or
                            1040 <= symbol_code <= 171 or
                            97 <= symbol_code <= 122 or
                            65 <= symbol_code <= 90):
                        break
                    elif snippet[index - 1].isdigit():
                        break
                    elif snippet[index - 1] in '!,.:;?':
                        snippet[index - 1] = '.'
                        dot = True
                        break

                index -= 1

            if dot:
                self.__snippet = ''.join(snippet[:index]) + '..'
            else:
                self.__snippet = ''.join(snippet[:index]) + '...'

    def get_snippet(self):
        return self.__snippet

    def get_title(self):
        return self.__title if self.__title else self.__h1
