from config import BaseConfig
from grammar import Grammar


def remove_left_recursion_direct(non_term, filename):
    print('-' * 80)
    print('Eliminating direct (immediate) left recursion\n')
    grammar = Grammar()
    grammar.load_from_json(BaseConfig.grammars_dir + filename)
    grammar.print_info(header='i')
    grammar.remove_left_recursion_direct_symbol(non_term)
    grammar.print_info(header='o')


def remove_left_recursion_indirect(filename):
    print('-' * 80)
    print('Eliminating indirect left recursion\n')
    grammar = Grammar()
    grammar.load_from_json(BaseConfig.grammars_dir + filename)
    grammar.print_info(header='i')
    grammar.remove_left_recursion_indirect()
    grammar.print_info(header='o')


def left_factoring(filename):
    print('-' * 80)
    print('Left factoring\n')
    grammar = Grammar()
    grammar.load_from_json(BaseConfig.grammars_dir + filename)
    grammar.print_info(header='i')
    grammar.left_factoring()
    grammar.print_info(header='o')


def remove_eps_productions(filename):
    print('-' * 80)
    print('Eliminating epsilon-productions\n')
    grammar = Grammar()
    grammar.load_from_json(BaseConfig.grammars_dir + filename)
    grammar.print_info(header='i')
    grammar.remove_eps_productions()
    grammar.print_info(header='o')


if __name__ == '__main__':
    remove_left_recursion_direct('S', 'grammar1.json')
    remove_left_recursion_indirect('grammar1.json')
    left_factoring('grammar2.json')
    remove_eps_productions('grammar3.json')
