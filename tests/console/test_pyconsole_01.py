# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk


# my modules and packages
from tkinter_console.console.pyconsole import PyConsole

if __name__ == '__main__':
    root = tk.Tk()
    root.title("PyConsole Test01 - prompt")

    console = PyConsole(root, locals(), wrap='none').init()
    info    = tk.StringVar()
    label   = ttk.Label(root, textvariable=info)

    # set prompt
    console.set_prompt_string(normal="$$$", wait='...')

    label.pack(fill=tk.X)
    console.pack(fill=tk.BOTH, expand=True)

    console.focus()

    def loop():
        global info
        i = console.index(tk.INSERT)
        s = console.get(i)
        row, pos = i.split('.')
        info.set("(row, pos)=({row}, {pos})='{value}'".format(
            row=row, pos=pos, value=s if s != '\n' else ''))
        console.after(50, loop)

    console.after(50, loop)

    root.mainloop()

