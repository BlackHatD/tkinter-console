# -*- coding:utf-8 -*-
import code
import ctypes
import threading
import tkinter as tk
from typing import Optional, Callable


# my modules and packages
from tkinter_console.utils.scrolledtext import ScrolledTextEx
from tkinter_console.utils.decorator import std_forker


class PyConsole(ScrolledTextEx):

    def __init__(self, master, _locals, **kwargs):
        super(PyConsole, self).__init__(master=master, **kwargs)

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
        self.__committed_strings: Optional[list] = None
        self.__committed_strings_history         = []


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


    def __init_prompt(self):
        """ initialize prompt """
        # set prompt string
        self.__used_prompt_string = self._prompt_string['normal']

        # set wait flag as False
        self.__wait_flag = False

        # delete strings on the line
        self.delete('.'.join([self.__get_current_row(), '0']), 'end-1c')

        # clear committed strings
        self.__committed_strings = []

        # prompt
        self.prompt()


    def init(self):
        """ initialization method

        Returns:
            PyConsole: instance

        """
        # init prompt
        self.__init_prompt()

        # run insert checker
        self.__check_insert_walker()

        # bind
        self.__bind_checking_action()
        self.__bind_ctr_c()
        self.bind('<Return>', self.__do_pressed_enter_key)

        return self



    def prompt(self) -> None:
        """ prompt

        Prompt '>>>' at the normal state, else '...' by default
        """
        self.mark_set(self._prompt_mark, tk.END)
        self.mark_gravity(self._prompt_mark, tk.RIGHT)

        if self.__wait_flag is False:
            self.__used_prompt_string = self._prompt_string['normal']
            self.insert(tk.END, self.__used_prompt_string)
        else:
            self.__used_prompt_string = self._prompt_string['wait']
            self.insert(tk.END, self.__used_prompt_string)

        self.mark_gravity(self._prompt_mark, tk.LEFT)


    def __get_current_line(self) -> list:
        """ return (row,pos) """
        return self.index(tk.INSERT).split('.')

    def __get_current_row(self) -> str:
        """ return current row """
        return self.__get_current_line()[0]

    def __get_current_pos(self) -> str:
        """ return current insert pos """
        return self.__get_current_line()[1]

    def __get_command_strings(self):
        """ get only command strings """
        row, pos      = self.__get_current_line()
        prompt_length = len(self.__used_prompt_string)
        return self.get('.'.join([row, str(prompt_length)]), tk.END)


    def __bind_ctr_c(self, func: Optional[Callable] = None) -> None:
        """ for bind Control-c """
        def default_func(e):
            self.__init_prompt()

        self.bind('<Control-c>', func if func else default_func)


    def __do_pressed_enter_key(self, event=None):
        """ if pressed enter key, execute the inputted command """
        # execute the inputted strings
        self.__execute_command_as_thread()
        return self.__do_not_do_anything()


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
            row, pos = self.__get_current_line()
            prompt_length = len(self.__used_prompt_string)

            if int(pos) < prompt_length:
                line = '.'.join([row, str(prompt_length)])
                self.mark_set(tk.INSERT, line)

            #TODO: color print

            self.after(rotate_time, checker)

        self.after(rotate_time, checker)



    def __bind_checking_action(self) -> None:
        """ bind checking action

        - press key
            - prevent the input position from going before the prompt
            - not allowed 'up' and 'down' key

        - click
            prevent the input position moves to the cursor

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
        def _get_history(press='up'):
            # TODO: insert command into history

            press = press.lower()

            command = self.__get_command_strings()
            if command not in self.__committed_strings_history:
                self.__committed_strings_history.append(command)

            if press == 'up':
                pass
            elif press == 'down':
                pass

            return self.__do_not_do_anything()

        def _press_up_key(e):
            return _get_history(press='up')

        def _press_down_key(e):
            return _get_history(press='down')

        # bind
        self.bind('<KeyPress>', _press_key)
        self.bind('<Up>'      , _press_up_key)
        self.bind('<Down>'    , _press_down_key)

        # bind click event
        self.bind('<ButtonPress>'  , lambda e: _on_click(state='disable'))
        self.bind('<ButtonRelease>', lambda e: _on_click(state='normal'))


    def __execute_command_as_thread(self):
        """ for infinite loop handling """
        def _wrapper():
            # set thread id
            thread_id = threading.current_thread().native_id
            self.__threading_pool[thread_id] = thread_id

            try:
                # bind kill thread to ctr+c
                self.__bind_ctr_c(lambda e: self.__kill_thread(thread_id))

                # execute
                self.__execute_command()

            finally:
                # reset bind
                self.__bind_ctr_c()

            self.__threading_pool.pop(thread_id)

        # check running thread
        if len(self.__threading_pool) == 0:
            threading.Thread(target=_wrapper).start()


    def __execute_command(self) -> None:
        """ execute command

        1. get an inputted strings.
        2. execute the compiled command, if is not state 'wait'.
        3. insert a result into text widget.
        4. prompt.

        """

        def _commit_to():
            command = self.__get_command_strings()

            # add new line
            self.insert(tk.INSERT, '\n')

            return command

        def _callback(result):
            # set result
            self.__result = result

        @std_forker(callback=_callback)
        def _execute():
            committed_string = _commit_to()
            striped          = committed_string.strip()

            # append a committed string
            self.__committed_strings.append(committed_string)
            self.__committed_strings_history.append(committed_string)

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
        for std, r in self.__result.items():
            if r != '':
                self.insert(tk.INSERT, self.__result.get(std))

        self.prompt()



    def __kill_thread(self, thread_id):
        # check thread
        if self.__threading_pool.get(thread_id):
            # kill the thread
            #   necessary importing ctypes
            #   https://www.delftstack.com/howto/python/python-kill-thread/
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                       ctypes.py_object(SystemExit))

            self.__threading_pool.pop(thread_id)
            self.__init_prompt()




