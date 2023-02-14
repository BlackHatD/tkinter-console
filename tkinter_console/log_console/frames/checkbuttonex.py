# -*- coding:utf-8
import tkinter as tk
from tkinter import ttk

__all__ = ['CheckButtonEx']

class CheckButtonEx(ttk.Checkbutton):
    def __init__(self, parent, *args, **kwargs):
        self.__flag: bool = kwargs.pop('flag')
        self.__text: str = kwargs['text']
        self.__var : tk.BooleanVar = tk.BooleanVar()

        self.__var.set(self.__flag)

        ttk.Checkbutton.__init__(self, parent, *args, **kwargs, variable=self.__var)

    def get(self):
        return self.__var.get()
