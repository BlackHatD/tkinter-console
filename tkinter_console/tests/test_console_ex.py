# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk
from logging import getLogger, DEBUG

from tkinter_console.log_console import LogConsoleExFrame

if __name__ == '__main__':
    logger = getLogger(__name__)
    logger.setLevel(DEBUG)

    def loglog():
        logger.debug('debug message')
        logger.info('info message')
        logger.warning('warn message')
        logger.error('error message')
        logger.critical('critical message')


    root = tk.Tk()
    root.title('LogConsoleExFrame Test')

    # for using 'expand_btn''s arg settings
    root.minsize(width=840, height=0)
    root.resizable(width=True, height=False)

    console_frame = LogConsoleExFrame(root, logger, expand_btn=True)
    console_frame.init().pack()
    console_frame.log_formatter = ' %(asctime)s\t[%(levelname)-8s]\t%(name)s\t%(filename)s\t%(funcName)s:%(lineno)d\t%(message)s'

    f = tk.LabelFrame(root, text='LOGLOG', foreground='white', background="blue", height=20, pady=5)
    f.pack(fill=tk.BOTH)
    ttk.Button(f, text="LOGGING", command=loglog).pack(fill=tk.X, expand=True)

    loglog()

    root.mainloop()

