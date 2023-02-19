# -*- coding:utf-8 -*-
import code
import tkinter as tk
from tkinter import ttk

# my modules and packages
from tkinter_console.utils.decorator import std_forker


if __name__ == '__main__':
    root = tk.Tk()

    shell = code.InteractiveConsole(locals())

    def callback(result):
        print(result)

    @std_forker(callback=callback)
    def on_run(e):
        command = command_entry.get()
        compiled = code.compile_command(command)

        shell.runcode(compiled)

    command_entry = ttk.Entry(root, width=100)
    command_entry.bind('<Return>', on_run)
    command_entry.pack(side=tk.LEFT, fill=tk.BOTH, pady=10)
    command_entry.insert(0, "print('hello')")
    command_entry.focus()

    root.mainloop()

