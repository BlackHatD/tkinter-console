# -*- coding:utf-8 -*-
import copy
import io
import sys
import traceback
from typing import Optional, Callable

__all__ = ['std_fork_decorator']

class std_fork_decorator:
    stdin     = sys.__stdin__.name
    stdout    = sys.__stdout__.name
    stderr    = sys.__stderr__.name
    traceback = traceback.__name__

    def __init__(self, callback: Optional[Callable] = None):
        # set functions
        self._func: Optional[Callable] = None
        self._callback = callback if callback else lambda output: output

        # for restoring
        self._org_stdin  = sys.stdin
        self._org_stdout = sys.stdout
        self._org_stderr = sys.stderr

        # function result
        self._result = None

        # for callback args
        self._org_output = {self.stdin      : ''
                            , self.stdout   : ''
                            , self.stderr   : ''
                            , self.traceback: ''}
        self._output    = copy.deepcopy(self._org_output)


    def __call__(self, func):
        # set function at first
        self._func = func

        def wrapper(*args, **kwargs):

            try:
                # override stdin, stdout, stderr
                self.__override_std()

                # run function and set return value
                self._result = self._func(*args, **kwargs)

            except Exception:
                # set traceback
                self._output[self.traceback] = traceback.format_exc()

            finally:
                # set output
                self.__set_output(name=self.stdin , std=sys.stdin)
                self.__set_output(name=self.stdout, std=sys.stdout)
                self.__set_output(name=self.stderr, std=sys.stderr)

                # restore std
                self.__restore_std()

                # run callback
                try:
                    self._callback(output=self._output)
                except Exception:
                    traceback.print_exc()

                # restore output
                self._output = copy.deepcopy(self._org_output)

            return self._result

        # return wrapper function's address
        return wrapper


    @staticmethod
    def __override_std():
        """ override std """
        sys.stdin  = io.TextIOWrapper(io.BytesIO(), sys.stdin.encoding)
        sys.stdout = io.TextIOWrapper(io.BytesIO(), sys.stdout.encoding)
        sys.stderr = io.TextIOWrapper(io.BytesIO(), sys.stderr.encoding)

    def __restore_std(self):
        """ restore std """
        sys.stdin  = self._org_stdin
        sys.stdout = self._org_stdout
        sys.stderr = self._org_stderr

    def __set_output(self, name, std):
        """ set output for callback function """
        std.seek(0)
        self._output[name] = std.read()
        std.close()

