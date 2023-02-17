# -*- coding:utf-8 -*-
import keyword
import tkinter as tk

from tkinter import ttk

# my modules and packages
from tkinter_console.console.pyconsole import PyConsole
from tkinter_console.utils.highlight import PATTERN, Highlight
from tkinter_console.utils.decorator import std_forker


if __name__ == '__main__':
    root = tk.Tk()
    root.title("PyConsole Test 02 - highlight")

    console = PyConsole(root, locals(), wrap='none').init()
    info    = tk.StringVar()
    label   = ttk.Label(root, textvariable=info)

    label.pack(fill=tk.X)
    console.pack(fill=tk.BOTH, expand=True)

    console.focus()

    # set prompt tags
    console.set_prompt_tag(foreground='blue')

    # set std tags
    console.set_std_tag(std_forker.stderr, foreground='red')
    console.set_std_tag(std_forker.traceback, foreground='red')

    # for normal highlighting
    normal_tag_dict = {}
    for k in keyword.kwlist:
        normal_tag_dict[k] = {'foreground': 'blue'}

    normal_tag_dict['print'] = {'foreground': 'gray'}

    # for regex highlighting
    regex_tag_dict = {
        'comment': {PATTERN: r'#.*', 'foreground': 'green'}
        , 'double_quotation': {PATTERN: r'".*?"', 'foreground': 'lime'}
        , 'single_quotation': {PATTERN: r"'.*?'", 'foreground': 'lime'}
    }


    # create highlight instance
    highlighter = Highlight()

    # attach highlighter
    console.attach_highlighter(highlighter)

    # set normal and regex dict
    console.highlighter.register_normal_tags(normal_tag_dict)
    console.highlighter.register_regex_tags(regex_tag_dict)


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

