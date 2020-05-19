import unittest

from config import TestConfig, BaseConfig
from grammar import Grammar


class TestGrammar(unittest.TestCase):
    # Грамматика из примера 2.23, Теория синтаксического анализа, перевода и компиляции, Т.1
    def test_remove_epsilon_productions_1(self):
        grammar = Grammar()
        grammar.load_from_json(TestConfig.grammars_dir + 'remove_eps_test1.json')
        grammar.remove_eps_productions()
        self.assertEqual(grammar.terms, ['a', 'b'])
        self.assertEqual(grammar.non_terms, ["S", "S'"])
        self.assertEqual(grammar.start_symbol, 'S' + BaseConfig.HATCH_SYMBOL)
        self.assertEqual(grammar.productions,
                         [['S', ['a', 'S', 'b', 'S']], ['S', ['a', 'b', 'S']], ['S', ['a', 'S', 'b']],
                          ['S', ['a', 'b']], ['S', ['b', 'S', 'a', 'S']], ['S', ['b', 'a', 'S']],
                          ['S', ['b', 'S', 'a']], ['S', ['b', 'a']], ["S'", ['S']], ["S'", ['ε']]])

    # Грамматика из упражнения 2.4.11, Теория синтаксического анализа, перевода и компиляции, Т.1
    def test_remove_epsilon_productions_2(self):
        grammar = Grammar()
        grammar.load_from_json(TestConfig.grammars_dir + 'remove_eps_test2.json')
        grammar.remove_eps_productions()
        self.assertEqual(grammar.terms, ['a', 'b'])
        self.assertEqual(grammar.non_terms, ["S", "A", "B", "C", "S'"])
        self.assertEqual(grammar.start_symbol, 'S' + BaseConfig.HATCH_SYMBOL)
        self.assertEqual(grammar.productions,
                         [['S', ['A', 'B', 'C']], ['S', ['B', 'C']], ['S', ['A', 'C']], ['S', ['A', 'B']], ['S', ['C']],
                          ['S', ['B']], ['S', ['A']], ['A', ['B', 'B']], ['A', ['B']], ['B', ['C', 'C']], ['B', ['C']],
                          ['B', ['a']], ['C', ['A', 'A']], ['C', ['A']], ['C', ['b']], ["S'", ['S']], ["S'", ['ε']]])

    # Грамматика из примера на стр. 17, CS 5641, Compiler Design, Fall '06
    def test_remove_left_recursion_direct(self):
        grammar = Grammar()
        grammar.load_from_json(TestConfig.grammars_dir + 'remove_left_recursion_test.json')
        grammar.remove_left_recursion_direct_symbol("S")
        self.assertEqual(grammar.terms, ['a', 'b'])
        self.assertEqual(grammar.non_terms, ['S', 'X', "S'"])
        self.assertEqual(grammar.start_symbol, 'S')
        self.assertEqual(grammar.productions,
                         [['X', ['X', 'b']], ['X', ['S', 'a']], ['X', ['b']],
                          ['S', ['X', 'S', "S'"]], ['S', ['a', "S'"]], ["S'", ['X', "S'"]],
                          ["S'", ['S', 'b', "S'"]], ["S'", ['ε']]])

    # Грамматика из примера на стр. 17, CS 5641, Compiler Design, Fall '06
    def test_remove_left_recursion_indirect(self):
        grammar = Grammar()
        grammar.load_from_json(TestConfig.grammars_dir + 'remove_left_recursion_test.json')
        grammar.remove_left_recursion_indirect()
        self.assertEqual(grammar.terms, ['a', 'b'])
        self.assertEqual(grammar.non_terms, ['S', 'X', "S'", "X'"])
        self.assertEqual(grammar.start_symbol, 'S')
        self.assertEqual(grammar.productions,
                         [['S', ['X', 'S', "S'"]], ['S', ['a', "S'"]],
                          ["S'", ['X', "S'"]], ["S'", ['S', 'b', "S'"]],
                          ["S'", ['ε']], ['X', ['b', "X'"]],
                          ['X', ['a', "S'", 'a', "X'"]], ["X'", ['b', "X'"]],
                          ["X'", ['S', "S'", 'a', "X'"]], ["X'", ['ε']]])

    # Грамматика из примера 4.11, Dragon book
    def test_remove_factoring(self):
        grammar = Grammar()
        grammar.load_from_json(TestConfig.grammars_dir + 'left_factoring_test.json')
        grammar.left_factoring()
        self.assertEqual(grammar.terms, ['i', 'e', 't', 'a', 'b'])
        self.assertEqual(grammar.non_terms, ['S', 'E', "S'"])
        self.assertEqual(grammar.start_symbol, 'S')
        self.assertEqual(grammar.productions,
                         [['E', ['b']], ['S', ['a']],
                          ['S', ['i', 'E', 't', 'S', "S'"]],
                          ["S'", ['e', 'S']], ["S'", ['ε']]])
