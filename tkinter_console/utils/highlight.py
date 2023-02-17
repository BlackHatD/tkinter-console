# -*- coding:utf-8 -*-
import tkinter as tk
from typing import Optional

__all__ = ['Highlight']


class Highlight:

    def __init__(self):
        self._master     : Optional[tk.Text] = None
        self.start_index : Optional[str]     = None
        self.end_index   : Optional[str]     = None

        self._normal_tags = {}
        self._regex_tags  = {}

    def attach(self, master: tk.Text
               , start_index='1.0', end_index=tk.END):
        self._master      = master
        self.start_index = start_index
        self.end_index   = end_index

        return self

    def __register_tags_by_configure(self, tags: dict):
        """ configure tags """
        for tag, kwargs in tags.items():
            self._master.tag_configure(tag, **kwargs)

    def __set_and_register_tag(self, self_tags: dict, tag, **kwargs):
        self_tags[tag] = kwargs
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


    def do_normal_highlight(self):
        for key, kwargs in self._normal_tags.items():
            # remove tag at first
            self._master.tag_remove(key, self.start_index, tk.END)

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


    def do_regex_highlight(self):
        count = tk.IntVar()
        regex_pattern = [r'".*"'        # double
                         , r'#.*'       # comment
                         , r"'''.*'''"
                         , r"'.*'"      # single
                         ]
        self._master.tag_configure('lime', foreground='lime')
        for pattern in regex_pattern:
            self._master.mark_set("start", self.start_index)
            self._master.mark_set("end", tk.END)
            num = int(regex_pattern.index(pattern))
            while True:
                index = self._master.search(pattern, "start", "end", count=count, regexp=True)
                if index == '':
                    break
                if num == 2:
                    self._master.tag_add('lime', index, "%s+%sc" % (index, count.get()))
                self._master.mark_set("start", "%s+%sc" % (index, count.get()))

