# -*- coding: utf-8 -*-

import cchardet as chardet

class Encoding(object):

    def detectecEncoding(self, text):
        unicod = text
        detected = cchardet.detect(text)

    @staticmethod
    def clean(text):
        encoding = detectecEncoding(text)
        if (encoding != 'utf-8'):
            text = text.encode('utf-8')
        return text