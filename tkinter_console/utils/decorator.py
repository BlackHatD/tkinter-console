# -*- coding:utf-8 -*-
import copy
import io
import sys
import traceback
from typing import Optional, Callable

__all__ = ['std_forker']

class std_forker:
    stdin     = sys.__stdin__.name
    stdout    = sys.__stdout__.name
    stderr    = sys.__stderr__.name
    traceback = traceback.__name__

    def __init__(self, callback: Optional[Callable] = None):

        # callback(result)
        self._callback = (callback
                          if callback
                          else lambda result: None)

        # for restoring
        self._org_stdin  = sys.stdin
        self._org_stdout = sys.stdout
        self._org_stderr = sys.stderr

        # function result
        self._func_result = None

        # for callback args
        self._result_fmt = {self.stdin      : ''
                            , self.stdout   : ''
                            , self.stderr   : ''
                            , self.traceback: ''}
        self._result     = copy.deepcopy(self._result_fmt)


    def __call__(self, func):

        def wrapper(*args, **kwargs):

            try:
                # override stdin, stdout, stderr
                self.__override_std()

                # run function and set return value
                self._func_result = func(*args, **kwargs)

            except Exception:
                # set traceback
                self._result[self.traceback] = traceback.format_exc()

            finally:
                # set output
                self.__set_output(name=self.stdin , std=sys.stdin)
                self.__set_output(name=self.stdout, std=sys.stdout)
                self.__set_output(name=self.stderr, std=sys.stderr)

                # restore std
                self.__restore_std()

                # run callback
                try:
                    self._callback(self._result)

                except Exception:
                    traceback.print_exc()

                # restore output
                self._result = copy.deepcopy(self._result_fmt)

            return self._func_result

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
        self._result[name] = std.read()
        std.close()

