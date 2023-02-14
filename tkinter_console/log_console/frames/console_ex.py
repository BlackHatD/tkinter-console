# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk
from typing import Optional
from logging import Logger, Formatter

# my modules and packages
from tkinter_console.log_console import LogConsoleFrame, INFO
from tkinter_console.log_console import LogSelectorFrame


__all__ = ['LogConsoleExFrame']


class LogConsoleExFrame(ttk.Frame):

    def __init__(self, master, logger: Logger
                 , level=INFO
                 , console_bg='black', auto_scroll=True
                 , log_formatter=Formatter('%(message)s')
                 , expand_btn=False):

        """ initializer

        Notes:
            If you set 'expand_btn=True',
            should use 'resizable(width=True, height=False)'
            and 'minsize(width=width, height=0).
            Should not use 'geometry(widthxheight)' method, because of that blank area is still existed.


        Args:
            master       : master (tk or ttk objects)
            logger       : logger object
            level        : default checkbutton flags. If set 'level=INFO', checkbuttons are checked except "DEBUG"
            console_bg   : console background color
            auto_scroll  : do auto scroll or not
            log_formatter: formatter
            expand_btn   : show expand button
        """
        super(LogConsoleExFrame, self).__init__(master=master)

        # set logger
        self.__logger        = logger
        self.__log_formatter = log_formatter

        # for selector
        # check button level
        self.__level = level

        # for console
        # do auto scroll or not
        self.__auto_scroll = auto_scroll
        self.__console_bg  = console_bg

        # widgets
        self.__w_selector_labelframe: Optional[ttk.LabelFrame] = None
        self.__w_console_labelframe : Optional[ttk.LabelFrame] = None

        self.w_selector_labelframe_config = {'text': 'Log text selector'}
        self.w_console_labelframe_config  = {'text': 'Log console'}

        # inner frames
        self.__w_console_inner_frame : Optional[LogConsoleFrame]  = None
        self.__w_selector_inner_frame: Optional[LogSelectorFrame] = None


        # show expand button or not
        self.__expand_flag         = expand_btn
        self.__expand_text         = {'expand': u"□", 'reduce': u"━"}
        self.__expand_textvariable = tk.StringVar()
        self.__expand_textvariable.set(self.__expand_text['reduce'])

        self.__w_expand_button : Optional[ttk.Button] = None

        # create widgets
        self.__create_widgets()


    @property
    def log_formatter(self):
        return self.__log_formatter

    @log_formatter.setter
    def log_formatter(self, log_formatter: str | Formatter):
        self.__w_console_inner_frame.log_formatter = log_formatter
        self.__log_formatter = self.__w_console_inner_frame.log_formatter


    @property
    def selector_labelframe(self) -> ttk.LabelFrame:
        """ ttk.LabelFrame: selector label frame """
        return self.__w_selector_labelframe

    @property
    def selector_inner_frame(self) -> ttk.Frame:
        """ ttk.Frame: selector frame """
        return self.__w_selector_inner_frame

    @property
    def console_inner_frame(self) -> ttk.Frame:
        """ ttk.Frame: console frame """
        return self.__w_console_inner_frame

    @property
    def console_labelframe(self) -> ttk.LabelFrame:
        """ ttk.LabelFrame: console label frame """
        return self.__w_console_labelframe

    @property
    def console_background(self) -> str:
        """ str: console background color """
        return self.__console_bg

    @console_background.setter
    def console_background(self, color):
        if self.__w_console_inner_frame:
            self.__w_console_inner_frame.set_background(color)
        self.__console_bg = color


    def init(self):
        """ initialization method

        Returns:
            LogConsoleExFrame: instance
        """
        self.__w_selector_labelframe.configure(**self.w_selector_labelframe_config)
        self.__w_console_labelframe.configure(**self.w_console_labelframe_config)

        # pack selector labelframe
        self.__w_selector_labelframe.pack_configure(pady=5)
        self.__w_selector_labelframe.pack(fill=tk.BOTH)

        # pack console labelframe
        # the reason, why the method is used, is
        # because of the method is used in expand method.
        self.__pack_console_labelframe()

        # setting pack configure
        self.pack_configure(fill=tk.BOTH, expand=True)

        return self


    def __pack_console_labelframe(self):
        self.__w_console_labelframe.pack(fill=tk.BOTH, expand=True)


    def __create_widgets(self):
        """ create below widgets

        - selector labelframe
        - selector inner frame from LogSelectorFrame
        - console labelframe
        - console inner frame from LogConsoleFrame class
        """

        # create label frames
        # selector
        self.__w_selector_labelframe = ttk.LabelFrame(self)
        self.__w_selector_labelframe.configure(padding=2)

        # console
        self.__w_console_labelframe = ttk.LabelFrame(self)
        self.__w_console_labelframe.configure(padding=2)

        # inner frames
        # initialize console at first
        self.__w_console_inner_frame = LogConsoleFrame(master=self.__w_console_labelframe
                                                       , logger=self.__logger
                                                       , auto_scroll=self.__auto_scroll)
        # initialize selector
        self.__w_selector_inner_frame = LogSelectorFrame(master=self.__w_selector_labelframe
                                                         , console=self.__w_console_inner_frame)

        # set checkbutton default check flag
        self.__w_selector_inner_frame.set_checkbutton_flag(self.__level)

        # set console format
        self.__w_console_inner_frame.log_formatter = self.__log_formatter
        # set console background color
        self.__w_console_inner_frame.scrolled_text_widget.configure(background=self.__console_bg)

        # pack selector
        self.__w_selector_inner_frame.init().pack(side=tk.LEFT)

        # create expand button
        if self.__expand_flag:
            self.__w_expand_button = ttk.Button(self.__w_selector_labelframe
                                                , textvariable=self.__expand_textvariable
                                                , width=3
                                                , command=self.__expand)
            self.__w_expand_button.pack_configure(pady=5)
            self.__w_expand_button.pack(side=tk.RIGHT)


        # pack console
        self.__w_console_inner_frame.init().pack()


    def __expand(self):
        if self.__w_console_labelframe.winfo_manager():
            # reduce (forget)
            self.__w_console_labelframe.forget()
            # set text variable as 'expand'
            self.__expand_textvariable.set(self.__expand_text['expand'])
        # is reduced
        else:
            # expand (pack)
            self.__pack_console_labelframe()
            # set text variable as 'reduce'
            self.__expand_textvariable.set(self.__expand_text['reduce'])



