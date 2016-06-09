import re
import pymorphy2
import math

from utils import normalize_spaces, word_tokenize
from stop_words import stop_words


class TextHandler:
    def __init__(self):
        self.sentences = ''
        self.frequencies = []
        self.bag_of_words = []
        self.length_of_bag = 0
        self.terms = set()
        self.text = ''
        self.title = ''
        self.h1 = ''
        self.h2 = ''
        self.h3 = ''
        self.h4 = ''
        self.h5 = ''
        self.h6 = ''
        self.boost_title = 3
        self.boost_h1 = 3
        self.boost_h2 = 2
        self.boost_h3 = 1
        self.boost_h4 = 1
        self.boost_h5 = 1
        self.boost_h6 = 1
        self.boost_text = 1
        self.analyzer = pymorphy2.MorphAnalyzer()

    def feed(self, text, **kwargs):
        self.__init__()

        self.text = TextHandler.clear_text(text)

        if kwargs['title']:
            self.title = TextHandler.clear_text(kwargs['title'])
        if kwargs['h1']:
            self.h1 = (TextHandler.clear_text(kwargs['h1']))
        if kwargs['h2']:
            for h2 in kwargs['h2']:
                self.h2 = ' '.join([TextHandler.clear_text(h2)])
        if kwargs['h3']:
            for h3 in kwargs['h3']:
                self.h3 = ' '.join([TextHandler.clear_text(h3)])
        if kwargs['h4']:
            for h4 in kwargs['h4']:
                self.h4 = ' '.join([TextHandler.clear_text(h4)])
        if kwargs['h5']:
            for h5 in kwargs['h5']:
                self.h5 = ' '.join([TextHandler.clear_text(h5)])
        if kwargs['h6']:
            for h6 in kwargs['h6']:
                self.h6 = ' '.join([TextHandler.clear_text(h6)])

        self.get_sentences(self.clear_text_for_snippets(self.text))
        self.tf()

    def get_terms_and_words(self, field):
        words = [
            self.analyzer.parse(word)[0].normal_form for word in word_tokenize(field)
            if word not in stop_words]

        terms = set(words)
        print('-----------------------')
        print(terms)
        print(words)
        print('-----------------------')
        return terms, words

    def tfc(self, field, boost, save_words=False):
        terms, words = self.get_terms_and_words(field)
        if save_words:
            self.bag_of_words = words
            self.length_of_bag = len(words)

        self.terms = self.terms.union(terms)
        frequency = {}
        for term in terms:
            frequency[term] = boost * (1 + math.log(words.count(term)))
        return frequency

    def get_term_positions(self, term):
        positions = []
        if term in self.bag_of_words:
            positions = [index for index in range(self.length_of_bag) if term == self.bag_of_words[index]]

        return positions

    def tf(self):
        tf_fields = [
            self.tfc(self.title, self.boost_title),
            self.tfc(self.h1, self.boost_h1),
            self.tfc(self.h2, self.boost_h2),
            self.tfc(self.h3, self.boost_h3),
            self.tfc(self.h4, self.boost_h4),
            self.tfc(self.h5, self.boost_h5),
            self.tfc(self.h6, self.boost_h6),
            self.tfc(self.text, self.boost_text, save_words=True)]

        for term in self.terms:
            frequencies = 0
            for dictionary in tf_fields:
                frequencies += dictionary.get(term, 0)

            self.frequencies.append([term, frequencies, self.get_term_positions(term)])

        self.frequencies.sort()

    def get_sentences(self, text):
        sentences = []
        kind_of_qoutes = set(('"', "'"))
        qoutes = False
        bracket = 0
        start_index = 0
        last_index = len(text) - 1
        ends = '!?;'
        dot = '.'
        may_be_end = ')'

        for index, char in enumerate(text):
            if char in kind_of_qoutes and not qoutes:
                qoutes = True
            elif char in kind_of_qoutes:
                qoutes = False
            elif char == '(':
                bracket += 1
            elif char == ')' and bracket > 0:
                bracket -= 1

            no_qoutes_and_brackets = bool(qoutes == 0 and bracket == 0)

            if index == last_index:
                sentences.append(text[start_index:index + 1].strip())
                break

            if char in ends and no_qoutes_and_brackets:
                if text[index + 1].isspace() and text[index + 2].isupper():
                    sentences.append(text[start_index:index + 1].strip())
                    start_index = index + 1

            if char == dot and no_qoutes_and_brackets:
                if (text[index + 1].isspace() and
                        (text[index - 1].islower() or
                            text[index - 1] in may_be_end or
                            text[index - 1] in kind_of_qoutes) and
                        text[index + 2].isupper()):
                    sentences.append(text[start_index:index + 1].strip())
                    start_index = index + 1

                elif (text[index - 1] == dot and
                        text[index - 2] == dot and
                        text[index + 1].isspace() and
                        text[index + 2].isupper()):
                    sentences.append(text[start_index:index + 1].strip())
                    start_index = index + 1

        self.sentences = '\n'.join(sentences)

    def clear_text_for_snippets(self, text):
        cleaner = re.compile('[\(].*?[\)]')
        punctuations = ',.;:!?'
        text = cleaner.sub('', text)
        for mark in punctuations:
            text = text.replace(' {0}'.format(mark), '{0}'.format(mark))
        return normalize_spaces(text)

    @staticmethod
    def clear_text(text):
        cleaner = re.compile('[\[].*?[\]]')
        return cleaner.sub('', text)

    @property
    def sentences(self):
        return self.sentences

    @property
    def frequencies(self):
        return self.frequencies


if __name__ == '__main__':
    import requests
    from htmlparser import Parser
    import time
    response = requests.get('http://devacademy.ru/posts/chego-ozhidat-ot-php7-chast-1/')
    content = response.content.decode('UTF-8')
    parser = Parser()
    parser.feed(content, response.url)

    start = time.time()

    txthandler = TextHandler()
    txthandler.feed(
        parser.text,
        title=parser.title,
        h1=parser.h1[0],
        h2=parser.h2,
        h3=parser.h3,
        h4=parser.h4,
        h5=parser.h5,
        h6=parser.h6)

    for x in txthandler.frequencies:
        print(x)
    print(txthandler.sentences)
    print("Time ", time.time() - start)
