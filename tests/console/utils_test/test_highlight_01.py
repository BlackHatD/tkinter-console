# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# my modules and packages
from tkinter_console.utils.highlight import Highlight


if __name__ == '__main__':

    key_dict = {'while': {'background': 'yellow'}}

    root = tk.Tk()
    root.attributes("-topmost", True)

    # create text widget
    text = ScrolledText(root)
    text.pack(fill=tk.BOTH, expand=True)
    text.focus()

    # create highlight object
    highlighter = Highlight()
    highlighter.attach(text)
    highlighter.register_normal_tags(key_dict)

    def do_highlight():
        def wrapper():
            highlighter.do_normal_highlighting()

            root.after(10, wrapper)
        root.after(10, wrapper)


    do_highlight()
    root.mainloop()