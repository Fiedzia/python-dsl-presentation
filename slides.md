!SLIDE

## Create your own DSL with Python
## Introduction to parser generators

!SLIDE

## About me

* Search engineer at CV-Library (cv-library.co.uk)
* I am working with a lot of text data using Python to process it

Maciej Dziardziel (fiedzia@gmail.com)

!SLIDE

## "A domain-specific language (DSL) is a computer language specialized to a particular application domain." (wikipedia)

!SLIDE left

## DSL Examples

* HTML
* CSS
* SQL
* Django ORM
* Programming languages

(programming languages are out of scope of this presentation, but you can use the tools we discuss today to design and process them)

!SLIDE left

## Reasons to create your own DSL and related tools:

* Provide easy to understand/write/process way of encoding domain-specific-knowledge
* You work with people not familiar with programming languages
* programming languge you are using is not suitable to work with given domain
* You want to process existing code for some DSL in a way no existing tool supports

!SLIDE left

## My motivation

* There are many job types, every type has its own terminology and concepts
* We needed a way to write down this knowledge to build set of job categories and assign them to jobs
* People who have this knowledge are not developers, so they needed simple tools they can work with easily
* We decided to create set of rules, where each rule may define conditions and actions
* rule may contain arbitrarily complex conditions

!SLIDE

## Rule example:

~~~~
    Conditions:
        title "python" and ("developer" or "programmer")
    Actions:
        add category "it/developers/python"
~~~~


!SLIDE left

## Now, how do I...

* parse this text into form usable in python
* generate Python code for it
* ensure rules are valid according to definition of our DSL

!SLIDE

## Version 1 - just use Python


~~~~{python}
    if "python" in job.title and ("developer" in job.title or "programmer" in job.title):
        job.labels.add("it/developers/python")
~~~~

!SLIDE left

## Pros:

* It just works
* Full power of Python
* Good error messages

## Cons:

* Full power of Python...
* Error messages understandable ... if you understan python
* Users (who are not developers) will need to understand enormous amount of Python concepts
* Code is tied to single implementation, its variables and datastructures
* Code is hard to analyze and modify
* Code is hard to optimize
* Its very easy to make all kinds of mistakes
* Running arbitrary code is dangerous


!SLIDE

## Let's see what Python really did for us:

~~~~{python}
    #cat code1_python_function.py

    def is_it_python_job(job):

        if "python" in job.title and ("developer" in job.title or "programmer" in job.title):
            job.labels.add("it/developers/python")
~~~~


!SLIDE


~~~~{python}
import code1_python_function

code1_python_function.is_it_python_job
>>> <function code1_python_function.is_it_python_job>

type(code1_python_function.is_it_python_job.__code__)
>>> code

import dis
dis.dis(code1_python_function.is_it_python_job)

>>> 0 LOAD_CONST               1 ('python')
>>> 3 LOAD_FAST                0 (job)
>>> 6 LOAD_ATTR                0 (title)
>>> 9 COMPARE_OP               6 (in)
>>> ...
~~~~

!SLIDE

~~~~{python}
code1_python_function.is_it_python_job.__code__.co_code
>> b'd\x01\x00|\x00\x00j\x00\x00k\x06\x00r@\x00d\x02\x00|\x00\x00j\x00\x00k\x06\x00s-\x00d\x03\x00|\x00\x00j\x00\x00k\x06\x00r@\x00|\x00\x00j\x01\x00j\x02\x00d\x04\x00\x83\x01\x00\x01n\x00\x00d\x00\x00S'
~~~~

!SLIDE

## Working with AST

~~~~
Help on function parse in module ast:

parse(source, filename='<unknown>', mode='exec')
    Parse the source into an AST node.
    Equivalent to compile(source, filename, mode, PyCF_ONLY_AST).

~~~~

!SLIDE

~~~~{python}
    import ast
    expr = ast.parse("2+2", "", "eval")

    ast.dump(expr)
    >>> 'Expression(body=BinOp(left=Num(n=2), op=Add(), right=Num(n=2)))'

    list(ast.walk(expr))

    >>> [<_ast.Expression at 0x7efef1c30630>,
    >>>  <_ast.BinOp at 0x7efef1c306a0>,
    >>>  <_ast.Num at 0x7efef1c30a90>,
    >>>  <_ast.Add at 0x7efef4f03da0>,
    >>>  <_ast.Num at 0x7efef1c306d8>]

    expr = ast.parse('"python" and ("developer" or "programmer")', "", "eval")
    ast.dump(expr)

    >>> "Expression(body=BoolOp(op=And(), values=[Str(s='python'), BoolOp(op=Or(), values=[Str(s='developer'), Str(s='programmer')])]))"
~~~~

!SLIDE

## Version 2: use subset of Python

~~~~{python}

import ast
ALLOWED_AST_NODES = (ast.Module,ast.Expression, ast.And, ast.Or, ast.Expr, ast.Str, ast.BoolOp, ast.UnaryOp, ast.Not)

def check_expr(expr_str):
    parsed = ast.parse(expr_str, '<rule>', 'eval')
    for node in ast.walk(parsed):
        if type(node) not in ALLOWED_AST_NODES:
            raise Exception('node type not allowed: {node_type}'.format(node_type=type(node)))

check_expr('"python" and "developer"')

>>>

check_expr('print(3)')

>>> Exception: node type not allowed: <class '_ast.Call'>

~~~~

!SLIDE

## AST modifications

~~~~{python}
class ASTConvertStrToCall(ast.NodeTransformer):
      """Transform 's' into contains('s')"""
  
      def visit_Str(self, node):
          return ast.copy_location(
              ast.Call(
                  func=ast.Name(id='contains', ctx=ast.Load()),
                  args=[ast.Str(node.s)],
                  keywords=[]
              ),
              node
          )

parsed = ast.parse(expr_str, '<rule>', 'eval')
tree = ASTConvertStrToCall().visit(parsed)
ast.fix_missing_locations(tree)
compiled = compile(tree, "<rule>", "eval")
namespace = {}
return eval(compiled, namespace)

~~~~
!SLIDE

## Full example

## Given arbitrary string like ' "python" and ("developer" or "programmer") '

## Generate python function that takes a string and return true if it matches our rules, false otherwise

code2_python_full_example.py

!SLIDE

## Benefits:

* We can reduce risk of running arbitrary code (but getting it right may be hard)
* We can use simple syntax and transform AST nodes into desired form

## Main problems

* We are still dealing with python code
* Python AST is too complex or too low-level for many needs
* We are limited by python syntax


!SLIDE left

## Version 3: let's use parser generator

What we want:

* Arbitrary syntax
* Arbitrary AST Node types


!SLIDE left

## What parser generator provide us:

* Language to define our DSL (usually its own DSL)
* Parser for our DSL
* Helper tools (debugging, visualisation)

!SLIDE

## Parser generators for Python 

https://wiki.python.org/moin/LanguageParsing


!SLIDE left

## Apreggo

http://igordejanovic.net/Arpeggio/

* Works with python3
* Well maintened
* Well documented
* Easy to use
* Good debugging tools


!SLIDE

## DSL definition - calculator

~~~{python}
number = r'\d*\.\d*|\d+'
factor = ("+" / "-")?
          (number / "(" expression ")")
term = factor (( "*" / "/") factor)*
expression = term (("+" / "-") term)*
calc = expression+ EOF
~~~

!SLIDE

## Generated AST for "2*(3+4)"

!["calc_ast"](./img/calc_ast.png "calc_ast")


!SLIDE

## Using AST

code3_arpeggio_calc.py

!SLIDE left

## Version 4: ANTLR


!SLIDE

## Links

* [This presentation](http://)
* [Arpeggio](http://igordejanovic.net/Arpeggio/)
* [ANTLR](www.antlr.org)
* [List of parser generators for Python](https://wiki.python.org/moin/LanguageParsing)



!SLIDE

## Any questions?
