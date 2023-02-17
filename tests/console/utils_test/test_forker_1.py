# -*- coding:utf-8 -*-
import code

# my modules and packages
from tkinter_console.utils.decorator import std_forker


if __name__ == '__main__':
    shell = code.InteractiveConsole(locals())

    def callback(result):
        print(result)
        print(result.get(std_forker.stdout))

    @std_forker(callback=callback)
    def on_run():
        command = "print('hello')"
        compiled = code.compile_command(command)

        shell.runcode(compiled)

        return "successfully"

    print(on_run())
