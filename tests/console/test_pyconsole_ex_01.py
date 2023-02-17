# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter_console import PyConsoleEx

if __name__ == '__main__':
    root = tk.Tk()
    root.title('PyConsoleEx Test01')

    console = PyConsoleEx(root, locals())
    console.init().pack()
    console.focus()

    root.mainloop()


