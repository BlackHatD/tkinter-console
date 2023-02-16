# -*- coding:utf-8 -*-
import code
import ctypes
import threading
import tkinter as tk
from typing import Optional, Callable


# my modules and packages
from tkinter_console.utils.scrolledtext import ScrolledTextEx
from tkinter_console.utils.decorator import std_forker
from tkinter_console.utils.history import History


__all__ = ['PyConsole']


class PyConsole(ScrolledTextEx):

    def __init__(self, master, _locals, **kwargs):
        super(PyConsole, self).__init__(master=master, **kwargs)

        self.__NEWLINE = '\n'

        # create interactive console instance
        self._shell = code.InteractiveConsole(_locals)
        self.__result: Optional[dict] = None

        self._prompt_mark   = 'prompt'
        self._prompt_string = {'normal': '>>> ', 'wait': '... '}

        # this parameter will be switched '>>>' or '...'
        # (set in '__init_prompt' method at the first time)
        self.__used_prompt_string: Optional[str] = None

        # for infinite loop handling
        self.__threading_pool = {}

        # wait flag (set in '__init_prompt' method at the first time)
        #   if an inputted the command includes ':' at the end
        #   set this flag
        self.__wait_flag: Optional[bool] = None

        # committed string list (set in '__init_prompt' method at the first time)
        #   if is the waiting stat, appended command strings
        self.__committed_strings: Optional[list]  = None
        # for getting command in history
        self.__committed_string_history: History = History()


    @property
    def prompt_string(self) -> dict:
        """ :obj: 'dict' of :obj:'str': prompt string """
        return self._prompt_string


    def set_prompt_string(self, normal, wait='...', add_last_space=True):
        """ set prompt string """
        space = ' ' if add_last_space else ''
        self._prompt_string['normal'] = normal + space
        self._prompt_string['wait']   = wait   + space

        # initialize prompt
        self.__init_prompt()


    def init(self):
        """ initialization method

        Returns:
            PyConsole: instance

        """
        # init prompt
        self.__init_prompt()

        # run walker
        self.__check_insert_walker()

        # bind
        self.__bind_checking_action()
        self.__bind_ctr_c()
        self.bind('<Return>', self.__do_pressed_enter_key)

        return self


    def __init_prompt(self):
        """ initialize prompt """
        # set prompt string
        self.__used_prompt_string = self._prompt_string['normal']

        # set wait flag as False
        self.__wait_flag = False

        # delete strings on the line except prompt
        self.__delete_line()

        # clear committed strings
        self.__committed_strings = []

        # prompt
        self.__prompt()



    def __prompt(self) -> None:
        """ prompt

        Prompt '>>> ' at the normal state, else '... ' by default
        """
        self.mark_set(self._prompt_mark, tk.END)
        self.mark_gravity(self._prompt_mark, tk.RIGHT)

        if self.__wait_flag is False:
            self.__used_prompt_string = self._prompt_string['normal']

        else:
            self.__used_prompt_string = self._prompt_string['wait']

        self.insert(tk.END, self.__used_prompt_string)

        self.mark_gravity(self._prompt_mark, tk.LEFT)


    def __do_pressed_enter_key(self, event=None):
        """ if pressed enter key, execute the inputted command """
        # execute the inputted strings
        self.__execute_command_as_thread()
        return self.__do_not_do_anything()


    def __get_current_index(self) -> list:
        """ return (row,pos) """
        return self.index(tk.INSERT).split('.')

    def __get_current_row(self) -> str:
        """ return current row """
        return self.__get_current_index()[0]

    def __get_current_pos(self) -> str:
        """ return current insert pos """
        return self.__get_current_index()[1]

    def __get_prompt_end_index(self) -> str:
        """ get prompt end line """
        row, pos      = self.__get_current_index()
        prompt_length = len(self.__used_prompt_string)
        return '.'.join([row, str(prompt_length)])

    def __get_command_string(self) -> str:
        """ get only command strings """
        return self.get(self.__get_prompt_end_index(), tk.END)

    def __delete_line(self) -> None:
        """ delete command line """
        self.delete(self.__get_prompt_end_index(), 'end-1c')

    def __write_command(self, command: str) -> None:
        """ write command string into text widget """
        self.__delete_line()
        self.insert(tk.INSERT, command if command else '')


    def __bind_ctr_c(self, func: Optional[Callable] = None) -> None:
        """ for bind Control-c """

        # inner function
        def default_func(e):
            if self.__wait_flag:
                self.insert(tk.INSERT, self.__NEWLINE)
            self.__init_prompt()

        self.bind('<Control-c>', func if func else default_func)


    def __add_history(self, command: str) -> None:
        """ add a command in the history """
        # right strip at first
        command = command.rstrip()
        history = self.__committed_string_history

        # check the command for whether adding or not
        if command != history.current():
            if command != history.get_index(-1):
                self.__committed_string_history.add(command)


    @staticmethod
    def __do_not_do_anything(event=None):
        """ please Tk, don't do anything... """
        return 'break'


    def __check_insert_walker(self
                              , rotate_time=20  # ms
                              ) -> None:
        # inner function
        def checker():
            # for prevent the input position from going before the prompt
            #   input keys are checked in '__bind_checking_action'
            #   but bellow patterns can't be checked
            #     'fn' + 'home' key and so on...
            #   so in the function check these patterns
            row, pos = self.__get_current_index()
            prompt_length = len(self.__used_prompt_string)

            if int(pos) < prompt_length:
                line = '.'.join([row, str(prompt_length)])
                self.mark_set(tk.INSERT, line)

            #TODO-#1: color print

            self.after(rotate_time, checker)

        self.after(rotate_time, checker)



    def __bind_checking_action(self) -> None:
        """ bind checking action

        - press key
            - prevent the input position from going before the prompt.
            - up   : insert a prev string from history.
            - down : insert a next string from history.

        - click
            prevent the input position moves to the cursor.

        """

        # inner function
        def _press_key(event):
            state: int  = event.state if hasattr(event, 'state') else 0
            keysym: str = event.keysym.lower()
            # other patterns are checked in '__check_insert_walker'
            if (keysym in ('backspace', 'left', 'home')
                    # for ctl+h
                    or state == 4):

                pos = self.__get_current_pos()
                # check position
                #   '>>>|ABC' : allowed
                #   '>>|>ABC' : not allowed
                if int(pos) < (len(self.__used_prompt_string) + 1):
                    return self.__do_not_do_anything()

        # inner function
        def _on_click(state):
            self.configure(state=state)
            self.mark_set(tk.INSERT, 'end - 1c')

        # inner function
        def _write_history_command(press='up'):
            # add the command into the history at first
            self.__add_history(self.__get_command_string())

            history = self.__committed_string_history
            # undo
            if press == 'up':
                self.__write_command(history.prev())
            # redo
            elif press == 'down':
                self.__write_command(history.next())

            return self.__do_not_do_anything()

        # inner function
        def _press_up_key(e):
            return _write_history_command(press='up')

        # inner function
        def _press_down_key(e):
            return _write_history_command(press='down')

        # bind
        self.bind('<KeyPress>', _press_key)
        self.bind('<Up>'      , _press_up_key)
        self.bind('<Down>'    , _press_down_key)

        # bind click event
        self.bind('<ButtonPress>'  , lambda e: _on_click(state='disable'))
        self.bind('<ButtonRelease>', lambda e: _on_click(state='normal'))


    def __execute_command_as_thread(self):
        """ for infinite loop handling """

        # inner function
        def _execute_wrapper():
            # set thread id
            thread_id = threading.current_thread().native_id
            self.__threading_pool[thread_id] = thread_id

            def _do_kill(e):
                if self.__threading_pool.get(thread_id):
                    self.__kill_thread(thread_id)
                    self.__threading_pool.pop(thread_id)
                    self.__init_prompt()

            try:
                # bind kill thread to ctr+c
                self.__bind_ctr_c(_do_kill)

                # execute
                self.__execute_command()

            finally:
                # reset bind
                self.__bind_ctr_c()

                # double check
                #   reason why double check is
                #   if ctr+'c' is pressed, in '__kill_thread' method,
                #   the thread_id is popped
                if self.__threading_pool.get(thread_id):
                    self.__threading_pool.pop(thread_id)


        # check running thread
        if len(self.__threading_pool) == 0:
            threading.Thread(target=_execute_wrapper).start()


    def __execute_command(self) -> None:
        """ execute command

        1. commit an inputted string into the executor.
        2. add the committed string into the history
        3. compile the committed string, and execute it, if is not state 'wait'.
        4. insert a result into the text widget.
        5. auto scroll.
        6. prompt.

        """

        # inner function
        def _commit():
            command = self.__get_command_string()

            # insert a new line
            self.insert(tk.INSERT, self.__NEWLINE)

            return command

        # inner function
        def _callback(result):
            # set result
            self.__result = result

        # inner function
        @std_forker(callback=_callback)
        def _execute():
            # commit string
            committed_string = _commit()
            striped          = committed_string.strip()

            # append a committed string
            self.__committed_strings.append(committed_string)
            # add command into the history
            self.__add_history(committed_string)

            # wait executing command
            if striped.endswith(':'):
                # set wait flag
                self.__wait_flag = True

            # execute the command
            elif (self.__wait_flag is False) or (striped == ''):
                try:
                    # compile and execute the command
                    compiled = code.compile_command(''.join(self.__committed_strings))
                    self._shell.runcode(compiled)

                finally:
                    # set wait flag
                    self.__wait_flag  = False

                    # clear committed strings
                    self.__committed_strings.clear()

                    # add history '' and set index at the last
                    history = self.__committed_string_history
                    self.__add_history('')
                    history._i = (len(history.get_history())-1)


        # execute run function
        _execute()

        # dump
        for std, r in self.__result.items():
            #TODO-1#: color print
            if r != '':
                self.insert(tk.INSERT, self.__result.get(std))

        # auto scroll
        self.yview(tk.END)

        # prompt
        self.__prompt()


    @staticmethod
    def __kill_thread(thread_id):
        # kill the thread
        #   necessary importing ctypes
        #   https://www.delftstack.com/howto/python/python-kill-thread/
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                   ctypes.py_object(SystemExit))





