# -*- coding:utf-8 -*-

__all__ = ['History']

class History(object):
    """
    References
        https://stackoverflow.com/questions/4146971/undo-and-redo-in-an-tkinter-entry-widget
    """

    def __init__(self, history_limit=10000):
        self._l     = ['']
        self._i     = 0
        self._limit = history_limit

    def get_index(self, i):
        return self._l[i]

    def get_history(self):
        return self._l

    def next(self):
        i = self._i + 1
        if i == len(self._l):
            return None
        self._i += 1
        return self._l[self._i]

    def prev(self):
        if self._i < 0:
            self._i = 0

        if self._i == 0:
            return None
        self._i -= 1
        return self._l[self._i]

    def add(self, s):
        if self._i < self._limit:
            self._i += 1
        else:
            self._l.pop(0)
        self._l.append(s)

    def current(self):
        return self._l[self._i]


