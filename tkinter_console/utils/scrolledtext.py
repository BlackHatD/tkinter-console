# -*- coding:utf-8 -*-
import tkinter as tk


__all__ = ['ScrolledTextEx']

class ScrolledTextEx(tk.Text):
    """ Customize the 'tkinter.scrolledtext' """

    def __init__(self, master=None, **kw):
        self.frame = tk.Frame(master)

        self.vbar_y = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.vbar_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)

        self.vbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        kw.update({'yscrollcommand': self.vbar_y.set})
        kw.update({'xscrollcommand': self.vbar_x.set})

        tk.Text.__init__(self, self.frame, **kw)

        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vbar_y['command'] = self.yview
        self.vbar_x['command'] = self.xview

        # Copy geometry methods of self.docs without overriding Text
        # methods -- hack!
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


