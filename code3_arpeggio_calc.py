from arpeggio.cleanpeg import ParserPEG
from arpeggio import visit_parse_tree


if __name__ == '__main__':

    debug = False
    calc_grammar = open('calc.peg').read()
    parser = ParserPEG(calc_grammar, "calc", debug=debug)
    input_expr = "2*(3+4)"
    parse_tree = parser.parse(input_expr)
