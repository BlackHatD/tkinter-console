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


class PyConsole(ScrolledTextEx):

    def __init__(self, master, _locals, **kwargs):
        super(PyConsole, self).__init__(master=master, **kwargs)

        # create interactive console instance
        self._shell = code.InteractiveConsole(_locals)
        self._result: Optional[dict] = None

        self._prompt_mark         = 'prompt'
        self._prompt_string       = {'normal': '>>> ', 'wait': '... '}

        # set prompt string at first
        # this parameter will be switched '>>>' or '...'
        self.__tmp_prompt_string  = self._prompt_string['normal']

        #-------------------------------------#
        # TODO: handling 'while True:'
        #-------------------------------------#
        # self.__timeout            = 10
        # self.__is_running         = False
        #-------------------------------------#

        # wait flag
        #   if an inputted the command includes ':'
        #   set this flag
        self.__wait_flag          = False

        # committed string list
        #   if is the waiting stat, appended command strings
        self.__committed_strings  = []


        self.init()


    @property
    def prompt_string(self) -> dict:
        """:obj: 'dict' of :obj:'str': prompt string """
        return self._prompt_string

    def set_prompt_string(self, normal, wait='...', add_space=True):
        """ set prompt string """
        space = ' ' if add_space else ''
        self._prompt_string['normal'] = normal + space
        self._prompt_string['wait']   = wait   + space


    def init(self):
        """ initialization method

        Returns:
            PyConsole: instance

        """
        # prompt at first
        self.prompt()

        # bind
        self.__bind_checking_action()
        self.bind('<Return>', self.__on_enter_key)

        return self

    def prompt(self) -> None:
        """ prompt

        Prompt '>>>' at the normal state, else '...' by default
        """
        self.mark_set(self._prompt_mark, tk.END)
        self.mark_gravity(self._prompt_mark, tk.LEFT)
        if self.__wait_flag is False:
            self.__tmp_prompt_string = self._prompt_string['normal']
            self.insert(tk.END, self.__tmp_prompt_string)
        else:
            self.__tmp_prompt_string = self._prompt_string['wait']
            self.insert(tk.END, self.__tmp_prompt_string)
        self.mark_gravity(self._prompt_mark, tk.RIGHT)


    def __on_enter_key(self, event=None):
        # execute the inputted strings
        self.__execute_command()
        return self.__do_not_do_anything()


    @staticmethod
    def __do_not_do_anything(event=None):
        """ please Tk, don't do anything... """
        return 'break'


    def __bind_checking_action(self) -> None:
        """ bind checking action

        - press key
            - prevent the input position from going before the prompt
            - now allowed up and down key

        - click
            prevent the input position moves to the cursor

        """
        def press_key(event):
            keysym = event.keysym.lower()
            if keysym in ('backspace', 'left', 'home'):
                _, pos = self.index(tk.INSERT).split('.')

                # check position
                #   '>>|>ABC' : not allowed
                if int(pos) < (len(self.__tmp_prompt_string) + 1):
                    return self.__do_not_do_anything()

                #-------------------------------------#
                # TODO: need a check logic
                #-------------------------------------#
                # '>>> ABC|' input 'home' key
                # '|>>> ABC'
                #-------------------------------------#


        def on_click(state):
            self.configure(state=state)
            self.mark_set(tk.INSERT, 'end - 1c')

        # bind
        self.bind('<KeyPress>', press_key)
        self.bind('<Up>'  , self.__do_not_do_anything)
        self.bind('<Down>', self.__do_not_do_anything)

        # bind click event
        self.bind('<ButtonPress>'  , lambda e: on_click('disable'))
        self.bind('<ButtonRelease>', lambda e: on_click('normal'))




    def __execute_command(self) -> None:
        """ execute command

        1. get an inputted strings.
        2. execute the compiled command, if is not state 'wait'.
        3. insert a result into text widget.
        4. prompt.

        """

        def _commit_to():
            row, _ = self.index(tk.INSERT).split('.')
            index = '.'.join([row, str(len(self.__tmp_prompt_string))])

            # add new line
            self.insert(tk.INSERT, '\n')

            return self.get(index, 'end - 1c')

        def _callback(output, _):
            print(output)
            self._result = output


        @std_forker(callback=_callback)
        def _execute():
            committed_string = _commit_to()
            striped          = committed_string.strip()

            # append a committed string
            self.__committed_strings.append(committed_string)

            # wait executing command
            if striped.endswith(':'):
                self.__wait_flag = True

            # execute the command
            elif (self.__wait_flag is False) or (striped == ''):
                try:
                    self.__is_running = True
                    compiled = code.compile_command(''.join(self.__committed_strings))
                    self._shell.runcode(compiled)

                finally:
                    self.__is_running = False
                    self.__wait_flag  = False

                    # clear committed strings
                    self.__committed_strings.clear()


        # execute run function
        _execute()

        # dump
        result = self._result
        for std, r in result.items():
            if r != '':
                self.insert(tk.INSERT, self._result.get(std))

        self.prompt()





