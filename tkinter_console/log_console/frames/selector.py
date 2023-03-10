# -*- coding:utf-8 -*-
import copy
import tkinter as tk

from tkinter import ttk
from logging import (
    Logger, getLevelName
)

# my modules and packages
from tkinter_console.log_console.frames.console import LogConsoleFrame
from tkinter_console.utils.checkbuttonex import CheckButtonEx


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
        # destroy checkbuttons if already exists
        self.destroy_checkbuttons()

        # create buttons
        self.__create_button_widgets()

        # run callback method at first
        self.__switch_callback()

        # setting pack configure
        self.pack_configure(fill=tk.X, expand=True)

        return self


    def destroy_checkbuttons(self):
        """ destroy checkbuttons """
        if len(self.__checkbuttons) > 0:
            for cb in self.__checkbuttons.values():
                cb.destroy()

    def set_checkbutton_flag(self, level, flag) -> None:
        """ set checkbutton flag """
        self._log_display_fmt[level]['flag'] = flag


    def set_checkbutton_flag_from(self, level) -> None:
        """ set checkbutton flag """
        for lev, value in copy.deepcopy(self._log_display_fmt).items():
            if level is None:
                self._log_display_fmt[lev]['flag'] = False
            else:
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

            cb = self.__checkbuttons.get(key)

            # is True
            if cb and cb.get():
                self.__switcher(key, False)

            # is False
            else:
                self.__switcher(key, True)

    def __switcher(self, tag, flag: bool):
        self._console.scrolled_text_widget.tag_config(tag, elide=flag)




