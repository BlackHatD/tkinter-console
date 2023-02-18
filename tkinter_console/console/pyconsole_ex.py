# -*- coding:utf-8 -*-
import os
import keyword
import builtins
import json
import shutil
from typing import Optional

# my modules and packages
from tkinter_console.utils import std_forker, Highlight
from tkinter_console.console.pyconsole import PyConsole

__all__ = ['PyConsoleEx']

class PyConsoleEx(PyConsole):
    """ Extended PyConsole """

    def __init__(self, master, _locals, **kwargs):
        super(PyConsoleEx, self).__init__(master=master, _locals=_locals, **kwargs)

        self.__config: Optional[dict] = None

        # load default config at first
        here = os.path.dirname(__file__)
        config = 'settings/console.json'
        self.__DEFAULT_CONFIG = os.path.abspath(os.path.join(here, config))
        self.load_config(self.__DEFAULT_CONFIG)

        # attach highlight object
        self.__highlighter = Highlight()

    @property
    def default_config(self) -> str:
        """ str: default config path """
        return self.__DEFAULT_CONFIG

    @property
    def config(self) -> dict:
        """ :obj:'dict' of :obj:'str' : config """
        return self.__config

    @config.setter
    def config(self, config_path: str) -> None:
        self.load_config(config_path)

    def init(self):
        """ customized initialization method

        Returns:
            PyConsoleEx: instance

        """

        super(PyConsoleEx, self).init()

        self.__setup_console()
        self.__setup_syntax_highlighting()

        return self

    def load_config(self, config_path: str) -> None:
        """ load json file

        Args:
            config_path: the json file path


        Raises:
            RuntimeError: if the file's extension is not '.json'

        """
        # check extension and the file exists, or not
        _, ext = os.path.splitext(config_path)
        if ext.lower() != '.json':
            raise RuntimeError("[!!] '{}' is not supported.".format(ext))

        elif not os.path.isfile(config_path):
            raise FileNotFoundError("[!!] the file doesn't exist!! - {}".format(config_path))

        # load the json file
        with open(config_path, mode='rt', encoding='utf-8') as fd:
            self.__config = json.load(fd)


    def generate_config(self) -> None:
        """ generate config """
        cfg  = os.path.dirname(self.__DEFAULT_CONFIG)
        dist = os.path.join(os.getcwd(), os.path.basename(cfg))
        shutil.copytree(cfg, dist)


    def __setup_console(self) -> None:
        """ setup console """
        console: dict = self.config['console']

        prompt : dict = console['prompt']
        std    : dict = console['std']

        self.configure(**console['kwargs'])

        self.set_prompt_string(normal=prompt['normal']
                               , wait=prompt['wait']
                               , add_last_space=False)
        self.set_prompt_tag(**prompt['kwargs'])

        for tag, values in std.items():
            kwargs = values['kwargs']

            if tag == 'stdin':
                std = std_forker.stdin
            elif tag == 'stdout':
                std = std_forker.stdout
            elif tag == 'stderr':
                std = std_forker.stderr
            elif tag == 'traceback':
                std = std_forker.traceback

            self.set_std_tag(std, **kwargs)


    def __setup_syntax_highlighting(self) -> None:
        """ setup syntax highlighting """

        # attach highlighter at first
        self.attach_highlighter(self.__highlighter)

        syntax          : dict = self.config['syntax']
        syntax_builtins : dict = syntax['builtins']
        syntax_normal   : dict = syntax['normal']
        syntax_regex    : dict = syntax['regex']

        py_keyword_dict: dict = {}

        # inner function
        def _set_building_keywords(l):
            py_keyword_dict.update({str(k): {**syntax_builtins['kwargs']} for k in l})

        # set builtin keywords
        _set_building_keywords(keyword.kwlist)
        _set_building_keywords(dir(builtins))

        # inner function
        def _register_tags(default_kwargs, obj, func):
            if len(obj) == 0:
                func(default_kwargs)
            else:
                for tag, values in obj.items():
                    kwargs = {str(k).lower(): v for k, v in values['kwargs'].items()}
                    default_kwargs.update({tag: kwargs})
                    func(default_kwargs)

        # register tags
        _register_tags(default_kwargs=py_keyword_dict
                       , obj=syntax_normal
                       , func=self.highlighter.register_normal_tags)
        _register_tags(default_kwargs={}
                       , obj=syntax_regex
                       , func=self.highlighter.register_regex_tags)




