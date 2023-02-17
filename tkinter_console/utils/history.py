# -*- coding:utf-8 -*-

__all__ = ['History']

class History(object):
    """
    References
        https://stackoverflow.com/questions/4146971/undo-and-redo-in-an-tkinter-entry-widget
    """

    def __init__(self, history_limit=10000):
        self._list     = ['']
        self._index    = 0
        self._limit = history_limit

    def get_index(self, i):
        return self._list[i]

    def get_history(self):
        return self._list

    def next(self):
        i = self._index + 1
        if i == len(self._list):
            return None
        self._index += 1
        return self._list[self._index]

    def prev(self):
        if self._index < 0:
            self._index = 0

        if self._index == 0:
            return None
        self._index -= 1
        return self._list[self._index]

    def add(self, s):
        if self._index < self._limit:
            self._index += 1
        else:
            self._list.pop(0)
        self._list.append(s)

    def current(self):
        return self._list[self._index]


