# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk
from logging import getLogger, DEBUG

# my modules and packages
from tkinter_console import LogConsoleFrame


if __name__ == '__main__':
    # create a logger object and set logger level
    logger = getLogger(__name__)
    logger.setLevel(level=DEBUG)

    # win size
    win_size = 640, 480

    # create root object
    root = tk.Tk()
    root.title('LogConsoleFrame Test')
    root.geometry('{}x{}'.format(*win_size))

    # create console frame
    console_frame = ttk.Label(root, text='Log console')
    console_frame.pack(expand=True, fill=tk.BOTH)

    # crate consoler inner frame
    console_inner_frame = LogConsoleFrame(console_frame, logger)
    console_inner_frame.set_display_debug_format(foreground="yellow")

    # set log format
    log_format = " %(asctime)s\t[%(levelname)-8s]\t%(name)s\t%(filename)s\t%(funcName)s:%(lineno)d\t%(message)s"
    console_inner_frame.log_formatter = log_format

    # initialize inner frame
    console_inner_frame.init().pack()


    # log some messages
    for i in range(5):
        if i % 5 == 0:
            logger.debug('debug message')
        logger.info('info message')
        logger.warning('warn message')
        logger.error('error message')
        logger.critical('critical message')


    # main loop
    root.mainloop()

