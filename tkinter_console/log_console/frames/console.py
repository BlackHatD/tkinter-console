# -*- coding:utf-8 -*-
import queue
from logging import (
    Logger, Formatter, LogRecord
    , NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
)

import tkinter as tk
from tkinter import ttk

# my modules and packages
from tkinter_console.log_console.frames.scrolledtext import ScrolledTextEx
from tkinter_console.log_console.handler.queue_handler import QueueHandler


__all__ = ['LogConsoleFrame'
           , 'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

class LogConsoleFrame(ttk.Frame):
    
    def __init__(self, master, logger: Logger, auto_scroll=True):
        super(LogConsoleFrame, self).__init__(master)

        # set scrolled text
        self._scrolled_text_widget = ScrolledTextEx(self, state='disabled'
                                                    , padx=1, wrap='none')
        self._scrolled_text_widget.configure(font='TkFixedFont')

        # logging settings
        self.logger          = logger
        self._log_formatter  = Formatter("%(message)s")

        # logging display format
        self._log_display_format = {
            DEBUG     : {'foreground': 'gray'}
            , INFO    : {'foreground': 'green'}
            , WARNING : {'foreground': 'orange'}
            , ERROR   : {'foreground': 'red'}
            , CRITICAL: {'foreground': 'red', 'underline': True}
        }

        # queue handler settings
        self.__poling_time = 100    # 100ms
        self.__auto_scroll = auto_scroll

        self.__queue         = queue.Queue()
        self.__queue_handler = QueueHandler(self.__queue)

    @property
    def scrolled_text_widget(self):
        return self._scrolled_text_widget

    @property
    def log_formatter(self) -> Formatter:
        """ Formatter: log formatter """
        return self._log_formatter


    @log_formatter.setter
    def log_formatter(self, log_formatter: str | Formatter):
        if isinstance(log_formatter, Formatter):
            self._log_formatter = log_formatter
        else:
            self._log_formatter = Formatter(log_formatter)

    @property
    def log_display_format(self) -> dict:
        """ dict: log display format """
        return self._log_display_format

    def __set_display_format(self, level, **kwargs):
        kwargs = {key.lower(): value for key, value in kwargs.items()}
        self._log_display_format[level].update(**kwargs)

    def set_display_debug_format(self, **kwargs) -> None:
        """ set display format for debug """
        self.__set_display_format(level=DEBUG, **kwargs)

    def set_display_info_format(self, **kwargs) -> None:
        """ set display format for info """
        self.__set_display_format(level=INFO, **kwargs)

    def set_display_warning_format(self, **kwargs) -> None:
        """ set display format for warning """
        self.__set_display_format(level=WARNING, **kwargs)

    def set_display_error_format(self, **kwargs) -> None:
        """ set display format for error """
        self.__set_display_format(level=ERROR, **kwargs)

    def set_display_critical_format(self, **kwargs) -> None:
        """ set display format for critical """
        self.__set_display_format(level=CRITICAL, **kwargs)


    def init(self):
        """ initialization method

        Returns:
            LogConsoleFrame: instance
        """
        # set the scrolled_text
        self._scrolled_text_widget.pack(expand=True, fill=tk.BOTH)
        for key, value in self._log_display_format.items():
            self._scrolled_text_widget.tag_config(str(key), value)


        # set a format and add the handler
        self.__queue_handler.setFormatter(self._log_formatter)
        self.logger.addHandler(self.__queue_handler)


        # start polling message from the queue
        self.after(self.__poling_time, self.__poll_log_queue)

        return self


    def __display(self, record: LogRecord):
        """ for displaying method """
        msg: QueueHandler.format = self.__queue_handler.format(record=record)
        self._scrolled_text_widget.configure(state='normal')
        self._scrolled_text_widget.insert(tk.END
                                          , "{msg}\n".format(msg=msg)
                                          , str(record.levelno))
        self._scrolled_text_widget.configure(state='disabled')

        # autoscroll to the bottom
        if self.__auto_scroll:
            self._scrolled_text_widget.yview(tk.END)

    def __poll_log_queue(self):
        """ for polling log method """
        # check every 100ms if there is anew message in the queue to display
        while not self.__queue.empty():
            msg: QueueHandler.format = self.__queue.get(block=False)
            self.__display(msg)
        self.after(self.__poling_time, self.__poll_log_queue)



