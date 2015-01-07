import io
import functools


prepend_string = """

import functools\n
import io\n


out = io.StringIO()\n

echo = print = functools.partial(print, file=out, end='')\n

del functools, io\n
"""

def custom_exec(string):
        pass

if __name__ == '__main__':
    string = 'print(\'hello\')\nout.write(\'you\')'
    c = compile(prepend_string + string, mode='exec', filename='<pyhp>')
    g = dict()
    r = exec(c, g)
    print(g['out'].getvalue())
