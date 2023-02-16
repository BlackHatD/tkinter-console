# -*- coding:utf-8 -*-
import code

# my modules and packages
from tkinter_console.utils.decorator import std_forker


if __name__ == '__main__':
    shell = code.InteractiveConsole(locals())

    def callback(output, result):
        print(output)
        print(output.get(std_forker.stdout))
        print(result)

    @std_forker(callback=callback)
    def on_run():
        command = "print('hello')"
        compiled = code.compile_command(command)

        shell.runcode(compiled)

        return "successfully"

    on_run()
