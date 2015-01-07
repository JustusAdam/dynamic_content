"""
DcHP - the dynamic_content hypertext preprocessor

Is a special html parser that finds <?dchp ?> blocks in your html file and
 executes the containing python code using exec().

Beware that in the future certain builtin methods may not be available anymore
 for security reasons.

some special properties:

    print(...) and echo(...) print objects (string representation) to the
     underlying html file
     This happens when the print(...) code executes ergo in whatever
     <?dchp ?> block it is called, be it directy or through some other
     function

    the global variables 'window' and 'dom' provide access to the
     previously parsed dom tree as python objects. These will soon(tm) be
     traversable with a jQuery-like syntax (.cildren(), .find() etc.)

    varibles, functions, classes etc. are local to the html file, not the
     <?dchp ?> block, meaning functions etc. defined in one <?dchp ?>
     block are accessible in subsequest <?dchp ?> blocks.
"""


from . import parser, evaluator
