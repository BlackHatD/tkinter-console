# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk
from logging import getLogger, DEBUG

# my modules and packages
from tkinter_console import LogConsoleFrame


logger = getLogger(__name__)

if __name__ == '__main__':
    logger.setLevel(level=DEBUG)

    win_size = 640, 480

    root = tk.Tk()
    root.title('Logging Handler Test')
    root.geometry('{}x{}'.format(*win_size))


    # console
    console_frame = ttk.Label(root, text='Log console')
    console_frame.pack(expand=True, fill=tk.BOTH)

    # initialize all frames
    console = LogConsoleFrame(console_frame, logger)
    console.set_display_debug_format(foreground="black")
    log_format = "%(asctime)s\t[%(levelname)-8s]\t%(name)s\t%(filename)s\t%(funcName)s:%(lineno)d\t%(message)s"
    console.log_formatter = log_format


    console.init().pack(fill=tk.BOTH, expand=True)


    # Log some messages
    for i in range(5):
        if i % 5 == 0:
            logger.debug('debug message')
        logger.info('info message')
        logger.warning('warn message')
        logger.error('error message')
        logger.critical('critical message')

    root.mainloop()

