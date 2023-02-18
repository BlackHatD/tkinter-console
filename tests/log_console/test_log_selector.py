# -*- coding:utf-8 -*-
from logging import getLogger, WARNING, ERROR
import tkinter as tk
from tkinter import ttk


# my modules and packages
from tkinter_console import LogConsoleFrame, LogSelectorFrame


if __name__ == '__main__':
    # create a logger object and set logger level
    logger = getLogger(__name__)
    logger.setLevel(WARNING)

    root = tk.Tk()
    root.title('LogSelectorFrame Test')
    root.geometry('1024x480')

    # selector frame
    selector_frame = ttk.LabelFrame(root, text="Log text selector")
    selector_frame.pack(fill=tk.BOTH)

    # console frame
    console_frame = ttk.Labelframe(root, text="Log console")
    console_frame.pack(fill=tk.BOTH, expand=True)

    # create console and selector instance
    console_inner_frame = LogConsoleFrame(console_frame, logger)
    console_inner_frame.scrolled_text_widget.configure(background='black')
    console_inner_frame.init().pack(fill=tk.BOTH, expand=True)

    selector_inner_frame = LogSelectorFrame(selector_frame, console_inner_frame)
    selector_inner_frame.set_checkbutton_flag_from(ERROR)
    selector_inner_frame.init().pack(fill=tk.BOTH, expand=True)


    # Log some messages
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')

    root.mainloop()

