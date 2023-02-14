# -*- coding:utf-8 -*-
import copy
import tkinter as tk

from typing import Optional
from tkinter import ttk
from logging import (
    Logger, getLevelName
)

# my modules and packages
from tkinter_console.log_console.frames.console import LogConsoleFrame
from tkinter_console.log_console.frames.checkbuttonex import CheckButtonEx


__all__ = ['LogSelectorFrame']

class LogSelectorFrame(ttk.Frame):

    def __init__(self, master, console: LogConsoleFrame):
        super(LogSelectorFrame, self).__init__(master=master)
        self._console         : LogConsoleFrame = console

        # add 'flag' key
        self._log_display_fmt : dict = {level: {'flag': True, **value}
                                        for level, value
                                        in copy.deepcopy(console.log_display_format).items()}

        self.__checkbuttons = {}

    def init(self):
        """ initialization method

        Returns:
            LogSelectorFrame: instance
        """
        # create buttons
        self.__create_button_widgets()

        # run callback method at first
        self.__switch_callback()

        # setting pack configure
        self.pack_configure(fill=tk.X, expand=True)

        return self


    def set_checkbutton_flag(self, level) -> None:
        """ set checkbutton flag """
        for lev, value in copy.deepcopy(self._log_display_fmt).items():
            if lev >= level:
                self._log_display_fmt[lev]['flag'] = True
            else:
                self._log_display_fmt[lev]['flag'] = False


    def __create_button_widgets(self) -> None:
        """ create button widgets """
        logger       : Logger = self._console.logger
        log_disp_fmt : dict   = {level: value
                                 for level, value in copy.deepcopy(self._log_display_fmt).items()
                                 if level >= logger.level
                                 }

        # create check buttons
        # and update check buttons dict
        for level, value in log_disp_fmt.items():
            cb = CheckButtonEx(self,
                               text=getLevelName(level)
                               , flag=value['flag']
                               , command=self.__switch_callback)
            cb.pack(side=tk.LEFT, padx=4, pady=2)

            # register a checkbutton
            self.__checkbuttons[level] = cb


    def __switch_callback(self):
        """ switch display a message, or not """
        for key, value in self._log_display_fmt.items():
            # true
            if self.__checkbuttons[key].get():
                self.__switcher(key, False)
            # false
            else:
                self.__switcher(key, True)

    def __switcher(self, tag, flag: bool):
        self._console.scrolled_text_widget.tag_config(tag, elide=flag)




