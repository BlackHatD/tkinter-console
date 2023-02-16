# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk


# my modules and packages
from tkinter_console.console.pyconsole import PyConsole


if __name__ == '__main__':
    root = tk.Tk()

    text = PyConsole(root, locals(), wrap='none')
    info  = tk.StringVar()
    label = ttk.Label(root, textvariable=info)

    label.pack(fill=tk.BOTH, expand=True)
    text.pack(fill=tk.BOTH, expand=True)

    text.focus()

    def loop():
        global info
        i = text.index(tk.INSERT)
        s = text.get(i)
        row, cursor = i.split('.')
        info.set("(row, cursor)=({row}, {cursor})='{value}'".format(
            row=row, cursor=cursor, value=s if s != '\n' else ''))
        text.after(50, loop)

    text.after(50, loop)



    root.mainloop()

