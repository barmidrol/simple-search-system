# coding=utf-8
import bz2
import re

def normalize_spaces(s):
    if not s:
        return ''
    return ' '.join(s.split())

def word_tokenize(field):
    splitter = re.compile(ur'[^\w\+-]')
    return [word.lower() for word in splitter.split(field) if word and word != '-' and not word.isspace()]

def word_tokenize_save_separators(field):
    splitter = re.compile(r'([^\w\+-])')
    return [word for word in splitter.split(field) if word]
