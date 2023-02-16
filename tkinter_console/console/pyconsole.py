# -*- coding:utf-8 -*-
import code
import hashlib
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk
from typing import Optional


# my modules and packages
from tkinter_console.utils.scrolledtext import ScrolledTextEx
from tkinter_console.utils.decorator import std_forker



class ConsoleFrame(ttk.Frame):
    def __init__(self, master):
        super(ConsoleFrame, self).__init__(master=master)




class ConsoleText(ScrolledTextEx):

    def __init__(self, master, _locals, **kwargs):
        super(ConsoleText, self).__init__(master=master, **kwargs)

        # create interactive console instance
        self._shell = code.InteractiveConsole(_locals)
        self._result: Optional[dict] = None

        self._prompt_string       = {'normal': '>>> ', 'wait': '... '}
        self._prompt_mark         = 'prompt'

        self.__prompt_string_tmp  = self._prompt_string['normal']
        self.__prompt_flag        = True
        self.__wait_flag          = False
        self.__committed_strings  = []

        self.init()

    @property
    def prompt_string(self):
        return self._prompt_string

    def set_prompt_string(self, normal, wait='...', add_space=True):
        if add_space:
            normal += ' '
            wait   += ' '
        self._prompt_string['normal'] = normal
        self._prompt_string['wait'] = wait


    def init(self):
        self.prompt()
        self.insert(tk.INSERT, 'for i in range(5): ')

        # bind
        self.__bind_checking_event()
        self.bind('<Return>', self._on_enter_key)



    def _run_command(self):

        def _inner_commit():
            row, _ = self.index(tk.INSERT).split('.')
            index = '.'.join([row, str(len(self.__prompt_string_tmp))])

            # add new line
            self.insert(tk.INSERT, '\n')

            return self.get(index, 'end - 1c')

        def _inner_callback(output, _):
            print(output)
            self._result = output


        @std_forker(callback=_inner_callback)
        def _inner_run():
            committed_string = _inner_commit()
            striped          = committed_string.strip()

            # append a committed string
            self.__committed_strings.append(committed_string)

            if striped.endswith(':'):
                self.__prompt_flag = False

            elif self.__prompt_flag or striped:
                try:
                    # execute
                    compiled = code.compile_command(''.join(self.__committed_strings))
                    self._shell.runcode(compiled)

                finally:
                    # set prompt flag
                    self.__prompt_flag = True

                    # clear committed strings
                    self.__committed_strings.clear()


        # execute run function
        _inner_run()

        # dump
        result = self._result
        for std, r in result.items():
            if r != '':
                self.insert(tk.INSERT, self._result.get(std))

        self.prompt()



    def _on_enter_key(self, event=None):
        # run command
        self._run_command()
        return 'break'



    def prompt(self):
        self.mark_set(self._prompt_mark, tk.END)
        self.mark_gravity(self._prompt_mark, tk.LEFT)
        if self.__prompt_flag:
            self.__prompt_string_tmp = self._prompt_string['normal']
            self.insert(tk.END, self.__prompt_string_tmp)
        else:
            self.__prompt_string_tmp = self._prompt_string['wait']
            self.insert(tk.END, self.__prompt_string_tmp)
        self.mark_gravity(self._prompt_mark, tk.RIGHT)


    def __bind_checking_event(self):

        def not_allowed(event=None):
            return 'break'

        def press_key(event):
            keysym = event.keysym.lower()
            if (keysym == 'backspace'
                    or keysym == 'left' or keysym == 'home'):
                _, pos = self.index(tk.INSERT).split('.')

                # check position
                #   '>>|>ABC' : not allowed
                if int(pos) < (len(self.__prompt_string_tmp) + 1):
                    return not_allowed()

        def on_click(state):
            self.configure(state=state)
            self.mark_set(tk.INSERT, 'end - 1c')

        # bind
        self.bind('<KeyPress>', press_key)
        self.bind('<Up>'      , not_allowed)
        self.bind('<Down>'    , not_allowed)

        # bind click event
        self.bind('<ButtonPress>'  , lambda e: on_click('disable'))
        self.bind('<ButtonRelease>', lambda e: on_click('normal'))



if __name__ == '__main__':
    root = tk.Tk()

    console_frame = ConsoleFrame(root)
    text = ConsoleText(console_frame, locals(), wrap='none')
    info  = tk.StringVar()
    label = ttk.Label(root, textvariable=info)

    label.pack(fill=tk.BOTH, expand=True)
    console_frame.pack(fill=tk.BOTH, expand=True)
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



