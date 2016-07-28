from arpeggio.cleanpeg import ParserPEG
from arpeggio import visit_parse_tree, PTNodeVisitor

class QueryVisitor(PTNodeVisitor):


    def __init__(self, *args, **kwargs):

        self.title = kwargs.pop('title')
        super().__init__(*args, **kwargs)

    def visit_phrase(self, node, children):
        return node.value.replace('"', '') in self.title

    def visit_neg_phrase(self, node, children):
        return node.value.replace('"', '') not in self.title


    def visit_factor(self, node, children):
        if len(children) == 1:
            result = children[0]

        elif len(children) == 3:
            result = children[1]
        return result

    def visit_neg_factor(self, node, children):
        if len(children) == 2:
            return not children[1]

        elif len(children) == 4:
            return not children[2]


    def visit_term(self, node, children):
        if len(children) == 1:
            return children[0]
        else:
            return all(children)

    def visit_neg_term(self, node, children):
        if len(children) == 2:
            return not children[1]
        else:
            return not all(children)


    def visit_expression(self, node, children):
        if len(children) == 1:
            result = children[0]
        else:
            result = any(children)
        return result

    def visit_neg_expression(self, node, children):
        if len(children) == 2:
            return not children[1]
        else:
            return not any(children)


if __name__ == '__main__':

    debug = False
    query_grammar = open('query.peg').read()
    parser = ParserPEG(query_grammar, "query", debug=debug)
    input_expr = '"python" and ( "developer" or "programmer")'
    parse_tree = parser.parse(input_expr)

    result = visit_parse_tree(parse_tree, QueryVisitor(debug=debug, title='python developer'))
    print(result)
    result = visit_parse_tree(parse_tree, QueryVisitor(debug=debug, title='java developer'))
    print(result)

