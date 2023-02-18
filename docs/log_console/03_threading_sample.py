# -*- coding:utf-8 -*-
import threading
import time
import tkinter as tk
from tkinter import ttk
from logging import (
    getLogger
    , DEBUG
    , INFO
)

# my modules and packages
from tkinter_console.log_console import LogConsoleExFrame

if __name__ == '__main__':
    # create a logger object and set logger level
    logger = getLogger(__name__)
    logger.setLevel(DEBUG)

    # define loglog method for using button as thread
    def loglog():

        def wrapper():
            while True:
                logger.debug('debug message')
                logger.info('info message')
                logger.warning('warn message')
                logger.error('error message')
                logger.critical('critical message')
                time.sleep(1)

        # start thread
        threading.Thread(target=wrapper, daemon=True).start()


    # create root object
    root = tk.Tk()
    root.title('Threading Sample')

    # create console frame
    console_frame = LogConsoleExFrame(root, logger, level=None)

    # set log format
    console_frame.log_formatter = '%(asctime)s\t[%(levelname)-8s]\t%(thread)+5s\t%(message)s'


    # check flag only debug
    console_frame.selector_inner_frame.set_checkbutton_flag(DEBUG, True)

    # initialize console frame
    console_frame.init()

    # for test
    button_frame = tk.LabelFrame(root, text='LOGLOG', foreground='white', background="blue", height=20, pady=5)
    button_frame.pack(fill=tk.BOTH)
    button = ttk.Button(button_frame, text="LOGGING", command=loglog)
    button.pack(fill=tk.X, expand=True)



    # mainloop
    root.mainloop()

