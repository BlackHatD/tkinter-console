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
from tkinter_console.utils.highlight import Highlight


__all__ = ['PyConsole']


class PyConsole(ScrolledTextEx):
    """ Python interactive console. """

    def __init__(self, master, _locals, **kwargs):
        """ initializer

        Args:
            master  : instance of TK widget
            _locals : locals()
            **kwargs: kwargs of tk.Text
        """
        super(PyConsole, self).__init__(master=master, **kwargs)

        self.__NEWLINE = '\n'

        # create interactive console instance
        self._shell = code.InteractiveConsole(_locals)
        self.__result: Optional[dict] = None

        # watchdogs settings
        self.__watchdogs_rotate    = 10  # ms
        self.__watchdogs_wait_flag = False

        # prompt settings
        self._prompt_normal_tag = 'normal'
        self._prompt_wait_tag   = 'wait'
        self._prompt_string     = {self._prompt_normal_tag: '>>> '
                                   , self._prompt_wait_tag: '... '}

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

        # for highlighting
        self.__highlighter: Optional[Highlight] = None
        self.__prompt_tags = {self._prompt_normal_tag: {}
                              , self._prompt_wait_tag: {}}

        self.__std_tags    = {std_forker.stdin      : {}
                              , std_forker.stdout   : {}
                              , std_forker.stderr   : {}
                              , std_forker.traceback: {}}

    def init(self):
        """ initialization method

        Returns:
            PyConsole: instance

        """

        # no wrap
        self.configure(wrap='none')

        # register tags at first
        self.__register_tags()

        # init prompt
        self.delete('0.0', tk.END)
        self.__init_prompt()

        # bind
        self.__bind_checking_action()
        self.__bind_ctr_c()
        self.bind('<Return>', self.__do_pressed_enter_key)

        # run watchdogs
        self.__run_watchdogs()

        # setting pack configure
        self.pack_configure(fill=tk.BOTH, expand=True)

        return self

    def set_watchdogs_rotation_time(self, ms) -> None:
        """ set watchdogs rotation time

        If you feel the process is too slow, use this method before initialize.

        Args:
            ms: ms
        """
        self.__watchdogs_rotate = ms

    @property
    def prompt_string(self) -> dict:
        """ :obj: 'dict' of :obj:'str': prompt string """
        return self._prompt_string

    def set_prompt_string(self, normal, wait='...', add_last_space=True):
        """ set prompt string """
        space = ' ' if add_last_space else ''
        self._prompt_string[self._prompt_normal_tag] = normal + space
        self._prompt_string[self._prompt_wait_tag]   = wait   + space

        # initialize prompt
        self.delete('0.0', tk.END)
        self.__init_prompt()

    @property
    def highlighter(self) -> Highlight | None:
        """ Highlight: highlight instance """
        return self.__highlighter

    def attach_highlighter(self, highlighter: Highlight):
        """ attach highlighter instance """
        self.__highlighter = highlighter
        highlighter.attach(master=self, start_index=self.__get_prompt_end_index())

    def set_prompt_tag(self, **kwargs) -> None:
        """ set prompt_tags """
        for values in self.__prompt_tags.values():
            values.update(**kwargs)
        self.__register_tags()

    def set_std_tag(self, std, **kwargs) -> None:
        """ set std tag

        Args:
            std      : use std_forker's class parameter
            **kwargs : foreground, background, and so on

        Examples:
            >> obj.set_std_tag(std_forker.stderr, foreground='red')

        """
        self.__std_tags[std].update(**kwargs)
        self.__register_tags()


    def __register_tags(self) -> None:
        """ register tags """
        def _register(tags):
            for k, v in tags.items():
                self.tag_configure(k, **v)
        _register(self.__prompt_tags)
        _register(self.__std_tags)


    def __add_prompt_tags(self):
        """ add prompt tags, it's used in '__prompt' method """
        for tag in self.__prompt_tags:
            start_index = self.__concat_row_pos(self.__get_current_row(), '0')
            end_index = self.__get_prompt_end_index()
            self.tag_add(tag, start_index, end_index)


    def __init_prompt(self):
        """ initialize prompt """
        # set prompt string
        self.__used_prompt_string = self._prompt_string[self._prompt_normal_tag]

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
        if self.__wait_flag is False:
            self.__used_prompt_string = self._prompt_string[self._prompt_normal_tag]

        else:
            self.__used_prompt_string = self._prompt_string[self._prompt_wait_tag]

        self.insert(tk.END, self.__used_prompt_string)


        # add prompt tags for highlighting
        self.__add_prompt_tags()


    def __do_pressed_enter_key(self, event=None):
        """ if pressed enter key, execute the inputted command """
        # execute the inputted strings
        self.__execute_command_as_thread()
        return self.__do_not_do_anything()

    @staticmethod
    def __concat_row_pos(row, pos) -> str:
        """ concat row and pos """
        return '.'.join((str(row), str(pos)))

    def __get_prompt_length(self) -> int:
        """ get prompt length """
        return len(self.__used_prompt_string)

    def __get_current_split_index(self) -> list:
        """ return (row,pos) """
        return self.index(tk.INSERT).split('.')

    def __get_current_row(self) -> int:
        """ return current row """
        return int(self.__get_current_split_index()[0])

    def __get_current_pos(self) -> int:
        """ return current insert pos """
        return int(self.__get_current_split_index()[1])

    def __get_prompt_end_index(self) -> str:
        """ get prompt end line """
        row           = self.__get_current_row()
        prompt_length = self.__get_prompt_length()
        return self.__concat_row_pos(row, prompt_length)

    def __delete_line(self) -> None:
        """ delete command line """
        self.delete(self.__get_prompt_end_index(), 'end-1c')

    def __get_command_string(self) -> str:
        """ get only command strings """
        return self.get(self.__get_prompt_end_index(), tk.END)

    def __write_command(self, command: str) -> None:
        """ write command string into text widget """
        self.__delete_line()
        self.insert(self.__get_prompt_end_index()
                    , command if command else '')

    def __clear_and_write_newline(self) -> None:
        """ clear and write a new line """
        self.__delete_line()
        self.insert(self.__get_prompt_end_index(), self.__NEWLINE)
        self.__init_prompt()
        self.yview(tk.END)

        # reset highlighting start index
        if self.highlighter:
            self.highlighter.start_index = self.__get_prompt_end_index()



    def __bind_ctr_c(self, func: Optional[Callable] = None) -> None:
        """ for bind Control-c """

        # inner function
        def default_func(e):
            self.__clear_and_write_newline()

        self.bind('<Control-c>', func if func else default_func)


    def __add_history(self, command: str) -> None:
        """ add a command in the history """
        # right strip at first
        command: str     = command.rstrip()
        history: History = self.__committed_string_history

        # check the command for whether adding or not
        if command != history.current():
            if command != history.get_index(-1):
                self.__committed_string_history.add(command)


    @staticmethod
    def __do_not_do_anything(event=None):
        """ please Tk, don't do anything... """
        return 'break'


    def __run_watchdogs(self) -> None:
        """ run watchdogs """

        # set rotate time
        rotate_time = self.__watchdogs_rotate

        # inner function
        def checker():
            if not self.__watchdogs_wait_flag:
                # for prevent the input position from going before the prompt
                #   input keys are checked in '__bind_checking_action'
                #   but bellow patterns can't be checked
                #     'fn' + 'home' key and so on...
                #   so in the function check these patterns
                if self.__get_current_pos() < self.__get_prompt_length():
                    self.mark_set(tk.INSERT, self.__get_prompt_end_index())

                # highlighting
                if self.__highlighter:
                    self.__highlighter.do_normal_highlighting()
                    self.__highlighter.do_regex_highlighting()

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
        def _do_pressed_key(event):
            state : int = event.state if hasattr(event, 'state') else 0
            keysym: str = event.keysym.lower()
            # other patterns are checked in '__run_watchdogs'
            if (keysym in ('backspace', 'left', 'home')
                    # for ctl+h
                    or state == 4):

                # check position
                #   '>>>|ABC' : allowed
                #   '>>|>ABC' : not allowed
                if self.__get_current_pos() <= self.__get_prompt_length():
                    return self.__do_not_do_anything()

            elif self.__get_current_pos() < self.__get_prompt_length():
                # check position
                #   1. '>>>ABCDEFG': press 'fn'+'home'+'delete'
                #   2. ''          : prompt string is deleted, so this check is necessary
                self.__delete_line()
                self.__prompt()

        # inner function
        def _write_history_command(press):
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
        def _on_click(state):
            self.configure(state=state)
            self.mark_set(tk.INSERT, 'end - 1c')

        # bind
        self.bind('<KeyPress>', _do_pressed_key)
        self.bind('<Up>'      , lambda e: _write_history_command(press='up'))
        self.bind('<Down>'    , lambda e: _write_history_command(press='down'))

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
                    # kill thread
                    self.__kill_thread(thread_id)
                    # pop thread id from threading pool
                    self.__threading_pool.pop(thread_id)
                    # clear and write new line
                    self.__clear_and_write_newline()
                    # set watchdogs flag
                    self.__watchdogs_wait_flag = False

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
            threading.Thread(target=_execute_wrapper, daemon=True).start()


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
            # move the insert position to end at first
            self.mark_set(tk.INSERT, tk.END)

            command: str = self.__get_command_string()

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
            committed_string: str = _commit()
            striped         : str = committed_string.strip()
            wait_keyword    : str = ':'

            # append a committed string
            self.__committed_strings.append(committed_string)
            # add command into the history
            self.__add_history(committed_string)

            # wait executing command
            if striped.endswith(wait_keyword):
                # set wait flag
                self.__wait_flag = True

            # execute the command
            elif (self.__wait_flag is False) or (striped == ''):

                # wait watchdogs for infinite loop handling
                self.__watchdogs_wait_flag = True

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
                    history: History = self.__committed_string_history
                    self.__add_history('')
                    # hack the history index
                    history._index = (len(history.get_history()) - 1)


        # execute run function
        _execute()


        # get the current row for highlighting
        row = self.__get_current_row()

        # dump
        for std, r in self.__result.items():
            if r != '':
                # insert result at first
                self.insert(tk.INSERT, self.__result.get(std))

                # add tags for highlighting
                start_index = self.__concat_row_pos(row, 0)
                end_index   = self.__concat_row_pos(self.__get_current_row(), tk.END)
                self.tag_add(std, start_index, end_index)


        # auto scroll
        self.yview(tk.END)

        # prompt
        self.__prompt()

        if self.highlighter:
            # set start index
            self.highlighter.start_index = self.__get_prompt_end_index()


        # run watchdogs
        # reason, why the code is written here,
        # is the dumped result may be highlighted
        self.__watchdogs_wait_flag = False


    @staticmethod
    def __kill_thread(thread_id):
        # kill the thread
        #   necessary importing ctypes
        #   https://www.delftstack.com/howto/python/python-kill-thread/
        resu = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                          ctypes.py_object(SystemExit))

        if resu  > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Failure in raising exception')




