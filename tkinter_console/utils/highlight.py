# -*- coding:utf-8 -*-
import copy
import tkinter as tk
from typing import Optional

__all__ = ['PATTERN', 'Highlight']

PATTERN = 'pattern'


class Highlight:

    def __init__(self):
        # exclude keys at 'tag_configure' is used
        self.__exclude_keys = (PATTERN,)

        self._master     : Optional[tk.Text] = None
        self.start_index : Optional[str]     = None
        self.end_index   : Optional[str]     = None

        self._normal_tags = {}
        self._regex_tags  = {}

        self.wait = False

    def attach(self, master: tk.Text
               , start_index='1.0', end_index=tk.END):
        self._master      = master
        self.start_index = start_index
        self.end_index   = end_index

        return self

    def __register_tags_by_configure(self, tags: dict):
        """ configure tags """
        for tag, kwargs in copy.deepcopy(tags).items():
            for exclude in self.__exclude_keys:
                if kwargs.get(exclude):
                    kwargs.pop(exclude)
            self._master.tag_configure(tag, **kwargs)

    def __set_and_register_tag(self, self_tags: dict, tag, **kwargs):
        self_tags[tag] = {str(k): str(v).lower() for k, v in kwargs.items()}
        self.__register_tags_by_configure(self_tags)

    def __set_and_register_tags(self, self_tags: dict, tags: dict):
        for tag, kwargs in tags.items():
            self.__set_and_register_tag(self_tags, tag, **kwargs)

    def register_normal_tag(self, tag, **kwargs) -> None:
        """ register normal tag """
        self.__set_and_register_tag(self._normal_tags, tag, **kwargs)

    def register_regex_tag(self, tag, **kwargs) -> None:
        """ register regex tag """
        self.__set_and_register_tag(self._regex_tags, tag, **kwargs)

    def register_normal_tags(self, tags: dict) -> None:
        """ register normal tags """
        self.__set_and_register_tags(self._normal_tags, tags)

    def register_regex_tags(self, tags: dict) -> None:
        """ register regex tags """
        self.__set_and_register_tags(self._regex_tags, tags)

    def delete_tags(self):
        """ delete tags """
        for tag, kwargs in self._normal_tags.items():
            self._master.tag_delete(tag)

    def restore_tags(self):
        """ restore tags """
        self.__register_tags_by_configure(self._normal_tags)
        self.__register_tags_by_configure(self._regex_tags)


    def do_normal_highlighting(self) -> None:
        """ normal highlighting """

        if self.wait:
            return

        for key, kwargs in self._normal_tags.items():
            # remove tag at first
            self._master.tag_remove(key, self.start_index, self.end_index)

            # set index
            index = self.start_index

            while True:
                pattern = r'\m{}\M'.format(key)

                # search
                index = self._master.search(pattern
                                            , index, regexp=True, stopindex=self.end_index)

                if not index:
                    break

                last_index = '%s+%sc' % (index, len(key))
                # add tag
                self._master.tag_add(key, index, last_index)
                # set last index
                index = last_index


    def do_regex_highlighting(self):
        """ regex highlighting """
        if self.wait:
            return

        count = tk.IntVar()

        for tag, kwargs in self._regex_tags.items():
            pattern = kwargs[PATTERN.lower()]

            self._master.mark_set('start', self.start_index)
            self._master.mark_set('end', self.end_index)

            while True:
                index = self._master.search(pattern, 'start', 'end', count=count, regexp=True)
                if index == '':
                    break
                self._master.tag_add(tag, index, '%s+%sc' % (index, count.get()))
                self._master.mark_set('start', '%s+%sc' % (index, count.get()))

