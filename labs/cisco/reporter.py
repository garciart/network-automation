# -*- coding: utf-8 -*-
"""My Reporter class.
"""

__all__ = ['Reporter', ]


class Reporter(object):
    # ANSI Color Constants
    __CLR = '\x1b[0m'
    __RED = '\x1b[31;1m'
    __GRN = '\x1b[32m'
    __YLW = '\x1b[33m'

    @staticmethod
    def step(text):
        print('Step: {0}'.format(text))

    @staticmethod
    def note(text):
        print('Note: {0}'.format(text))

    def warn(self, text):
        print(self.__YLW + '[WARN]: {0}'.format(text) + self.__CLR)

    def error(self, text=''):
        if text:
            print(self.__RED + '[FAIL]: {0}'.format(text) + self.__CLR)
        else:
            print(self.__RED + '[FAIL]' + self.__CLR)

    def success(self):
        print(self.__GRN + '[OK]' + self.__CLR)
