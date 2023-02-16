# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk
from logging import getLogger, DEBUG

# my modules and packages
from tkinter_console.log_console import LogConsoleExFrame

if __name__ == '__main__':
    # create a logger object and set logger level
    logger = getLogger(__name__)
    logger.setLevel(DEBUG)

    # define loglog method for using button
    def loglog():
        logger.debug('debug message')
        logger.info('info message')
        logger.warning('warn message')
        logger.error('error message')
        logger.critical('critical message')


    # create root object
    root = tk.Tk()
    root.title('LogConsoleExFrame Test')

    # for using 'expand_btn''s arg settings
    root.minsize(width=0, height=0)
    root.resizable(width=True, height=False)


    # create console frame
    console_frame = LogConsoleExFrame(root, logger
                                      , level=DEBUG
                                      , expand_btn=True)

    # set log format
    console_frame.log_formatter = '%(asctime)s\t[%(levelname)-8s]\t%(name)s\t%(filename)s\t%(funcName)s:%(lineno)d\t%(message)s'

    # initialize console frame at first
    console_frame.init().pack()



    # for test
    button_frame = tk.LabelFrame(root, text='LOGLOG', foreground='white', background="blue", height=20, pady=5)
    button_frame.pack(fill=tk.BOTH)
    button = ttk.Button(button_frame, text="LOGGING", command=loglog)
    button.pack(fill=tk.X, expand=True)

    # run loglog function at first
    loglog()


    # mainloop
    root.mainloop()

