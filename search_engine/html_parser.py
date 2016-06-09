import requests

from urlparse import urlparse
from lxml import html as lxml_html
from lxml.html.clean import Cleaner
from HTMLParser import HTMLParser

from utils import normalize_spaces


class HTMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.__result = []

    def handle_data(self, data):
        self.__result.append(data)

    def get_data(self):
        return ''.join(self.__result)


class Parser:
    MIN_TEXT_LENGTH = 25
    TEXT_LENGTH = 250

    def __init__(self):
        self.__html = ''
        self.__response_url = ''
        self.__candidate_chunks = []
        self.__useful_text_chunks = []
        self.__title = ''
        self.__links = []
        self.__h1 = []
        self.__h2 = []
        self.__h3 = []
        self.__h4 = []
        self.__h5 = []
        self.__h6 = []

    def feed(self, html, response_url):
        # reset instance attributes
        self.__init__()

        self.__response_url = response_url
        html_tree = lxml_html.fromstring(self.__clean_html(html))
        self.__get_headers_and_links(html_tree)
        self.__remove_bad_tagtrees(html_tree)
        self.__html = lxml_html.tostring(html_tree, method="html", encoding='unicode')

        del html_tree

        self.__get_candidate_chunks()
        self.__find_useful_text_chunks()

    def __clean_html(self, html):
        remove_tags = ['img']
        cleaner = Cleaner(
            scripts=True, javascript=True, comments=True,
            style=True, links=True, meta=True, add_nofollow=True,
            page_structure=False, processing_instructions=True,
            embedded=False, frames=False, forms=True, annoying_tags=False,
            remove_unknown_tags=False, safe_attrs_only=False, remove_tags=remove_tags)
        return cleaner.clean_html(html)

    def __html_splitlines(self):
        # just don't even try to understand this

        lines = []
        temp = ''

        for line in self.__html.splitlines():
            normalize_line = normalize_spaces(line)
            if normalize_line:
                if normalize_line[0] != '<' and temp:
                    temp += ' ' + normalize_line
                    if temp[-1] == '>':
                        lines.append(temp)
                        temp = ''
                elif normalize_line[0] != '<' and normalize_line[-1] != '>':
                    lines.append(normalize_line)
                elif normalize_line[0] != '<':
                    lines[-1] += ' ' + normalize_line
                elif normalize_line[-1] == '>' and temp:
                    temp += ' ' + normalize_line
                    lines.append(temp)
                    temp = ''
                elif normalize_line[-1] == '>':
                    lines.append(normalize_line)
                else:
                    temp += ' ' + normalize_line

        return lines

    def __get_candidate_chunks(self):
        for chunk in self.__html_splitlines():
            cleaned_chunk = normalize_spaces(self.__strip_tags(chunk))
            length_cleaned_chunk = len(cleaned_chunk)
            if length_cleaned_chunk > self.MIN_TEXT_LENGTH:
                marks = sum([cleaned_chunk.count(mark) for mark in '.,!?:;'])
                links_density = self.__get_link_density(chunk, length_cleaned_chunk)

                if marks > 0 and links_density < 0.5 and marks / length_cleaned_chunk < 0.1:
                    candidate = {}
                    candidate['length_with_tags'] = len(chunk)
                    candidate['text'] = cleaned_chunk
                    candidate['length_without_tags'] = length_cleaned_chunk
                    candidate['count_punctuation_marks'] = marks
                    candidate['links_density'] = links_density

                    self.__candidate_chunks.append(candidate)

    def __get_link_density(self, html_cnunk, length_cleaned_chunk):
        tree = lxml_html.fromstring(html_cnunk)
        links_length = len(''.join(([a.text_content().strip() for a in tree.xpath('//a')])))
        links_density = links_length / max(length_cleaned_chunk, 1)
        return links_density

    def __strip_tags(self, html):
        stripper = HTMLStripper()
        stripper.feed(html)
        return stripper.get_data()

    def __find_useful_text_chunks(self):
        for candidate in self.__candidate_chunks:
            can_append = False

            text_density = candidate['length_without_tags'] / candidate['length_with_tags']
            weight = (text_density + candidate['count_punctuation_marks'] / 100) + (1 - candidate['links_density'])
            if weight > 1.2 and candidate['links_density'] < 0.3:
                can_append = True
            elif (weight > 0.7 and candidate['links_density'] < 0.5 and
                    candidate['length_without_tags'] > self.TEXT_LENGTH):
                can_append = True

            if can_append:
                self.__useful_text_chunks.append(candidate['text'])

    def __get_headers_and_links(self, html_tree):

        try:
            self.__title = html_tree.xpath('//title/text()')[0]
        except IndexError:
            pass

        self.__h1 = [h1.text_content().strip() for h1 in html_tree.xpath('//h1')]
        self.__h2 = [h2.text_content().strip() for h2 in html_tree.xpath('//h2')]
        self.__h3 = [h3.text_content().strip() for h3 in html_tree.xpath('//h3')]
        self.__h4 = [h4.text_content().strip() for h4 in html_tree.xpath('//h4')]
        self.__h5 = [h5.text_content().strip() for h5 in html_tree.xpath('//h5')]
        self.__h6 = [h6.text_content().strip() for h6 in html_tree.xpath('//h6')]

        #for el, attr, link, pos in html_tree.iterlinks():
        #    link = urlparse.urldefrag(urlparse.unquote_plus(urlparse.urljoin(self.__response_url, link)))
        #    self.__links.append((el.text_content(), attr, link[0], pos))

    def __remove_bad_tagtrees(self, html_tree):
        remove_tagtree = [
            './/code', './/head', './/header', './/aside', './/footer', './/nav',
            './/title', './/h1', './/h2', './/h3', './/h4', './/h5', './/h6', './/pre'
        ]

        [element.drop_tree() for element in html_tree.xpath(" | ".join(remove_tagtree))]
        return html_tree

    @property
    def title(self):
        return self.__title

    @property
    def h1(self):
        return self.__h1

    @property
    def h2(self):
        return self.__h2

    @property
    def h3(self):
        return self.__h3

    @property
    def h4(self):
        return self.__h4

    @property
    def h5(self):
        return self.__h5

    @property
    def h6(self):
        return self.__h6

    @property
    def text(self):
        return ' '.join(self.__useful_text_chunks)

    @property
    def links(self):
        return self.__links
