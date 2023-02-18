# -*- coding:utf-8 -*-
import tkinter as tk

# my modules and packages
from tkinter_console import PyConsoleEx

if __name__ == '__main__':
    win_size = 640, 480

    root = tk.Tk()
    root.title('Quick start')
    root.geometry('{}x{}'.format(*win_size))

    # create an instance
    console = PyConsoleEx(master=root, _locals=locals())

    # initialize and pack
    console.init()
    console.pack()

    console.focus()

    root.mainloop()

