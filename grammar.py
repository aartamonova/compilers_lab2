import json
import itertools
import os

from config import BaseConfig


class Grammar:
    def __init__(self):
        self.terms = []
        self.non_terms = []
        self.start_symbol = None
        self.productions = []

    def _check_grammar(self):
        if not self.start_symbol or len(self.terms) < 1 or \
                len(self.non_terms) < 1 or len(self.productions) < 1:
            raise BaseException('Grammar is empty')

        if self.start_symbol not in self.non_terms:
            raise BaseException('Grammar is incorrect')

        if len(set(self.terms) & set(self.non_terms)) > 0:
            raise BaseException('Grammar is incorrect')

        for production in self.productions:
            if isinstance(production[0], list):
                raise BaseException('Grammar must be context free')

            if production[0] not in self.non_terms:
                raise BaseException('Grammar is incorrect')

    def _check_eps_productions(self):
        for production in self.productions:
            if BaseConfig.EPSILON_SYMBOL in production[1]:
                return True
        return False

    def _check_cycles(self):
        cycle_list = []
        for i, symbol in enumerate(self.non_terms):
            check_list = []
            cycle_list.append([symbol])
            while check_list != cycle_list[i]:
                check_list = cycle_list[i].copy()
                for production in self.productions:
                    if production[0] in cycle_list[i] and len(production[1]) == 1:
                        if production[1][0] in self.non_terms and production[1][0] not in cycle_list[i]:
                            cycle_list[i].append(production[1][0])

            cycle_list[i].pop(0)
            if len(cycle_list[i]) > 0:
                return True

        return False

    def _check_left_recursion_direct_symbol(self, symbol):
        """Проверка, есть ли хотя бы одна продукция вида A->Aα по
        заданному A"""
        for production in self.productions:
            if production[0] == symbol and production[1][0] == symbol:
                return True
        return False

    def _check_left_recursion_direct(self):
        """Проверка, есть ли хотя бы одна продукция вида A->Aα
        для всех A из множества нетерминалов"""
        for symbol in self.non_terms:
            if self._check_left_recursion_direct_symbol(symbol):
                return True
        return False

    def _pop_symbol_productions(self, symbol):
        """Удаление текущих продукций вида A->γ по заданному A
        и возврат их в виде списка"""
        if symbol not in self.non_terms:
            raise BaseException('Symbol must be nonterminal')

        new_productions = []
        symbol_productions = []
        for production in self.productions:
            if production[0] == symbol:
                symbol_productions.append(production)
            else:
                new_productions.append(production)

        self.productions = list(new_productions)
        return symbol_productions

    def _pop_left_right_productions(self, left, right):
        """Удаление текущих продукций вида A->Bγ по заданным
        A и B и возврат их в виде списка"""
        if left not in self.non_terms or right not in self.non_terms:
            raise BaseException('Symbol must be nonterminal')

        new_productions = []
        symbol_productions = []
        for production in self.productions:
            if production[0] == left and production[1][0] == right:
                symbol_productions.append(production)
            else:
                new_productions.append(production)

        self.productions = list(new_productions)
        return symbol_productions

    def _get_symbol_productions(self, symbol):
        if symbol not in self.non_terms:
            raise BaseException('Symbol must be nonterminal')

        symbol_productions = []
        for production in self.productions:
            if production[0] == symbol:
                symbol_productions.append(production)

        return symbol_productions

    def _get_max_prefix(self, symbol):
        """Поиск самого длинного общего префикса для двух или более продукций, в
         левой части которых находится нетерминал symbol"""

        if symbol not in self.non_terms:
            raise BaseException('Symbol must be nonterminal')

        # Правые части продукций, в левой части которых находится symbol
        right_parts = [x[1] for x in self._get_symbol_productions(symbol)]

        # Поиск всех возможных комбинаций правых частей продукций
        combinations = []
        for i in range(2, len(right_parts) + 1):
            for j in itertools.combinations(right_parts, i):
                combinations.append(list(j))

        # Поиск самого длинного общего префикса для двух или более
        # продукций для каждой возможной комбинации
        prefixes = []
        for combination in combinations:
            prefix = os.path.commonprefix(combination)
            if len(prefix) > 0 and prefix not in prefixes:
                prefixes.append(prefix)

        if len(prefixes) == 0:
            return None

        return list(max(prefixes))

    def remove_eps_productions(self):
        """Удаление эпсилон-продукций"""
        self._check_grammar()

        if not self._check_eps_productions():
            return

        # Получение списка нетерминалов, стоящих в левой части продукций
        # вида A->eps и удаление этих продукций
        eps_list = []
        for production in self.productions:
            if len(production[1]) == 1 and BaseConfig.EPSILON_SYMBOL in production[1]:
                if production[0] not in eps_list:
                    eps_list.append(production[0])
                del self.productions[self.productions.index(production)]

        # Получение списка нетерминалов, стоящих в левой части продукций
        # вида B->A, где каждый символ из А входит в eps_list
        check_list = []
        while eps_list != check_list:
            check_list = eps_list.copy()
            for production in self.productions:
                if set(production[1]).issubset(set(eps_list)) and production[0] not in eps_list:
                    eps_list.append(production[0])

        new_productions = []
        for production in self.productions:
            # Индексы нетерминалов из правой части этой продукции, которые есть в eps_list
            delete_indexes = []
            for i, symbol in enumerate(production[1]):
                if symbol in eps_list:
                    delete_indexes.append(i)

            if len(delete_indexes) > 0:
                if production not in new_productions:
                    new_productions.append(production)

                # Комбинации, полученные путем всех возможных исключений нетерминалов
                # из списка eps_list
                # Пример: из S->AaB следуют комбинации S->AaB, S->aB, S->Aa, S->a
                combinations = []
                for i in range(1, len(delete_indexes) + 1):
                    for j in itertools.combinations(delete_indexes, i):
                        combinations.append(list(j))

                for combination in combinations:
                    combination = sorted(combination, reverse=True)
                    new_right_part = list(production[1])
                    for index in combination:
                        del new_right_part[index]

                    new_production = [production[0], new_right_part]

                    # Не добавлять дубликаты и бессмысленные продукции типа A->A
                    if new_production not in new_productions and len(new_production[1]) > 0:
                        if len(new_production[1]) > 1 or (new_production[0] != new_production[1][0]):
                            new_productions.append(new_production)

            else:
                if production not in new_productions:
                    new_productions.append(production)

        # Если стартовый символ S находится в eps_list, добавить новый
        # стартовый символ S' и продукции S'->S, S'->eps
        if self.start_symbol in eps_list:
            new_start_symbol = str(self.start_symbol) + BaseConfig.HATCH_SYMBOL
            new_productions.append([new_start_symbol, [self.start_symbol]])
            new_productions.append([new_start_symbol, [BaseConfig.EPSILON_SYMBOL]])
            self.non_terms.append(new_start_symbol)
            self.start_symbol = new_start_symbol

        self.productions = list(new_productions)

    def remove_left_recursion_direct_symbol(self, symbol):
        """Удаление непосредственной левой рекурсии для нетерминала symbol"""

        if symbol not in self.non_terms:
            raise BaseException('Symbol must be nonterminal')

        if not self._check_left_recursion_direct_symbol(symbol):
            return

        symbol_productions = self._pop_symbol_productions(symbol)

        new_productions = []
        alpha_list = []
        beta_list = []

        # Составление двух списков, содержащих правую часть продукций, в
        # левой части которых находится нетерминал symbol:
        # alpha_list - правая часть продукций, начинающихся с symbol (без symbol)
        # beta_list - правая часть продукций, не начинающихся с symbol
        for production in symbol_productions:
            if production[1][0] == symbol:
                alpha_list.append(production[1][1:])
            else:
                beta_list.append(production[1])

        # Добавление нового нетерминала вида A'
        hatch_symbol = symbol + BaseConfig.HATCH_SYMBOL

        # Добавление новых продукций вида A-->βA' для каждого β
        for beta in beta_list:
            new_right_part = list(beta)
            new_right_part.append(hatch_symbol)
            new_productions.append([symbol, new_right_part])

        # Добавление новых продукций вида A'-->αA' для каждого α
        for alpha in alpha_list:
            new_right_part = list(alpha)
            new_right_part.append(hatch_symbol)
            new_productions.append([hatch_symbol, new_right_part])

        # Добавление продукции вида A'->ε
        new_productions.append([hatch_symbol, [BaseConfig.EPSILON_SYMBOL]])

        self.non_terms.append(hatch_symbol)
        self.productions.extend(new_productions)

    def remove_left_recursion_indirect(self, check_eps=True, check_cycles=True):
        if check_eps and self._check_eps_productions():
            raise BaseException('Remove eps productions first')

        if check_cycles and self._check_cycles():
            raise BaseException('Remove cycles first')

        non_terms = list(self.non_terms)

        for i in range(len(non_terms)):
            if i == 0:
                self.remove_left_recursion_direct_symbol(non_terms[i])

            for j in range(len(non_terms) - 1):
                new_productions = []
                # Правые части продукций вида Ai->Ajγ (без Aj)
                gamma_list = [x[1][1:] for x in self._pop_left_right_productions(non_terms[i], non_terms[j])]
                # Правые части всех продукций, в левой части которых находится Aj
                delta_list = [x[1] for x in self._get_symbol_productions(non_terms[j])]

                # Замена продукций
                for gamma in gamma_list:
                    for delta in delta_list:
                        new_productions.append([non_terms[i], delta + gamma])
                self.productions.extend(new_productions)
            self.remove_left_recursion_direct_symbol(non_terms[i])

    def left_factoring(self):
        self._check_grammar()

        new_non_terms = []
        for symbol in self.non_terms:
            new_productions = []
            max_prefix = self._get_max_prefix(symbol)
            while max_prefix:
                right_parts = [x[1] for x in self._pop_symbol_productions(symbol)]
                for right_part in right_parts:
                    if ''.join(right_part).startswith(''.join(max_prefix)):
                        # Часть тела продукции без общего префикса
                        without_prefix = right_part[len(max_prefix):]

                        if len(without_prefix) == 0:
                            without_prefix = [BaseConfig.EPSILON_SYMBOL]

                        # Добавление нового нетерминала вида A'
                        hatch_symbol = symbol + BaseConfig.HATCH_SYMBOL

                        if hatch_symbol not in new_non_terms:
                            new_non_terms.append(hatch_symbol)

                        # Добавление новых продукций
                        new_productions.append([hatch_symbol, without_prefix])
                        new_productions.append([symbol, list(max_prefix) + [hatch_symbol]])
                    else:
                        if [symbol, right_part] not in self.productions:
                            self.productions.append([symbol, right_part])

                max_prefix = self._get_max_prefix(symbol)
            self.productions.extend(new_productions)

        self.productions = [production[0] for production in itertools.groupby(sorted(self.productions))]
        self.non_terms.extend(new_non_terms)

    def load_from_json(self, filename):
        try:
            file = open(filename)
        except:
            raise FileNotFoundError('Unable to open JSON file')

        try:
            data = json.load(file)
        except:
            file.close()
            raise BaseException('Unable to parse JSON file')

        try:
            self.terms = data['terms']
            self.non_terms = data['non_terms']
            self.start_symbol = data['start_symbol']
            self.productions = data['productions']
        except:
            raise BaseException('Unable to parse JSON file')
        finally:
            file.close()

        for i, production in enumerate(self.productions):
            for j, symbol in enumerate(production[1]):
                if symbol == BaseConfig.EPSILON_SIGN:
                    production[1][j] = BaseConfig.EPSILON_SYMBOL

        self._check_grammar()

    def print_info(self, header=None):
        if header:
            if header == 'i':
                print('INPUT')
            elif header == 'o':
                print('OUTPUT')
            else:
                print(header)
        print('Terms:', ' '.join(self.terms))
        print('Non-terms:', ' '.join(self.non_terms))
        print('Start symbol:', str(self.start_symbol))
        print('Productions (' + str(len(self.productions)) + '): ', end='')
        for production in self.productions:
            print(str(production[0]) + '-->' + ''.join(production[1]) + '  ', end='')
        print('\n')
