# coding=utf-8
import bz2
import re

def normalize_spaces(s):
    if not s:
        return ''
    return ' '.join(s.split())


def word_tokenize(field):
    try:
        field = field.decode('utf-8')
    except:
        print('Cant decode')
    
    splitter = re.compile(ur'[^А-Яа-я\w\+-]')
    return [word.lower() for word in splitter.split(field) if word and word != '-' and not word.isspace()]

def word_tokenize_save_separators(field):
    splitter = re.compile(r'([^\w\+-])')
    return [word for word in splitter.split(field) if word]

def compress_data(data):
    if type(data) is not bytes:
        try:
            data = data.encode('utf-8')
        except Exception as err:
            print('Encode fail, error: ', err)

    return data


def decompress_data(data):
    return bz2.decompress(data)
