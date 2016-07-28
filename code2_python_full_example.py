import ast


class ASTConvertStrToCall(ast.NodeTransformer):
    """Transform 's' into contains(title, 's')"""

    def visit_Str(self, node):
        return ast.copy_location(
            ast.Call(
                func=ast.Name(id='contains', ctx=ast.Load()),
                args=[ast.Str(node.s)],
                keywords=[]
            ),
            node
        )


def dsl_to_func(code_str):
    """
    Convert string into python function 
    """

    parsed = ast.parse(code_str, '<rule>', 'eval')
    tree = ASTConvertStrToCall().visit(parsed)
    ast.fix_missing_locations(tree)
    compiled = compile(tree, "<rule>", "eval")

    def func(title):
        namespace = {
            'contains': lambda kw: kw in title
        }
    
        return eval(compiled, namespace)
    return func



if __name__ == '__main__':
    dsl_str = '"python" and ("developer" or "programmer")'
    func = dsl_to_func(dsl_str)
    print(func('python developer'))
    print(func('java developer'))
