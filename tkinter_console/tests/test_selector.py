# -*- coding:utf-8 -*-
import logging
from logging import getLogger, DEBUG, WARNING, ERROR
import tkinter as tk
from tkinter import ttk
from tkinter_console import *


if __name__ == '__main__':
    logger = getLogger(__name__)
    logger.setLevel(DEBUG)

    root = tk.Tk()
    root.title('Log Selector Test')
    root.geometry('1024x480')

    # selector frame
    selector_frame = ttk.LabelFrame(root, text="Log text disable")
    selector_frame.pack(fill=tk.BOTH)

    # console frame
    console_frame = ttk.Labelframe(root, text="Log console")
    console_frame.pack(fill=tk.BOTH, expand=True)

    # create console and selector instance
    console = LogConsoleFrame(console_frame, logger)
    console.scrolled_text_widget.configure(background='black')
    console.init().pack(fill=tk.BOTH, expand=True)

    selector = LogSelectorFrame(selector_frame, console)
    selector.set_checkbutton_flag(logging.CRITICAL)
    selector.init().pack(fill=tk.BOTH, expand=True)


    # Log some messages
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')

    root.mainloop()

