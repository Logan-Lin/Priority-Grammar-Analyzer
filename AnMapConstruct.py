import pandas as pd
import os

from utils import init_grammar


class AnMapConstruct:
    def __init__(self, grammar):
        self.grammar = grammar
        self.non_ts = grammar[~grammar.index.duplicated(keep='first')].index

        # first_dict is a python dict used to store FIRST(a) array corresponding to one non-terminal symbol and formula.
        # The dict's form is (non-terminal, formula) -> FIRST(a) list.
        self.first_dict = dict()

        # follow_dict is a python dict used to store FOLLOW(A) array.
        # The dict's form is non-terminal -> FOLLOW(a) set.
        self.follow_dict = dict()

    def get_all_formulas(self, non_t):
        """
        Returns all formulas corresponding to the specified non-terminal symbol.

        :param non_t: string, the non-terminal symbol.
        :return: list or pandas Series, all formulas corresponding to the specified non-terminal symbol
        """
        formulas = self.grammar.loc[non_t]
        formulas = formulas["formula"]
        if type(formulas).__name__ == "str":
            # If there is only one formula corresponding to the non-terminal symbol,
            # the returned 'formulas' could be string object.
            # Considering we have to traverse 'formulas', we turn it to a list here.
            formulas = [formulas]
        return formulas

    def construct_first(self):
        """
        Construct all non-terminal symbols and formulas' FIRST(a) array.
        """
        for non_t in self.non_ts:
            self.get_first(non_t)

        for non_t in self.non_ts:
            self.append_first(non_t)

        print("====FIRST(a) details====")
        print('{0:15}{1:}'.format("Formula", "First(a)"))
        for (non_t, formula), first in self.first_dict.items():
            print('{0:2}-> {1:10}{{{2:}}}'.format(non_t, formula, ", ".join(sorted(first))))
        print()

    def construct_follow(self, start_symbol='S'):
        """
        Construct all non-terminal symbols' FOLLOW(A) array.

        :param start_symbol: string, the start symbol of the grammar.
        """
        for non_t in self.non_ts:
            self.get_follow(non_t, start_symbol)

        for i in range(len(self.non_ts)):
            for non_t in self.non_ts:
                self.append_follow(non_t)

        print("====FOLLOW(A) details====")
        print('{0:6}{1:}'.format("Non-t", "FOLLOW(A)"))
        for non_t, follow in self.follow_dict.items():
            print('{0:6}{{{1:}}}'.format(non_t, ", ".join(sorted(follow))))
        print()

    def get_first(self, non_t, first_index=0):
        """
        Get a non-terminal symbols' all FIRST(a) array.
        Insert every formula's FIRST(a) into first_dict in the same time.

        :param non_t: str, non-terminal symbol.
        :param first_index: int, the index to fetch the first symbol.
            Used to skip non-terminal symbols that can be inferred to empty.
        :return: set, the non-terminal symbol's all FIRST(a) array.
        """
        # List 'first' is used to store the non-terminal symbol's all FIRST(a) array.
        first = set()
        for formula in self.get_all_formulas(non_t):
            # List 'formula_first' is used to store formula's FIRST(a) array.
            formula_first = set()
            formula_list = formula.split(" ")
            try:
                first_sym = formula_list[first_index]
            except IndexError:
                continue
            if first_sym.isupper():
                if 'e' in list(self.get_all_formulas(first_sym)):
                    # If the first symbol can be inferred to empty.
                    first |= self.get_first(non_t, first_index=first_index + 1)
                    formula_first |= self.get_first(non_t, first_index=first_index + 1)
                if not first_sym == non_t:
                    # The first symbol of formula is an upper character, which means it is an non-terminal symbol.
                    # In this case, we recursively search for corresponding FIRST(a) array.
                    first |= self.get_first(first_sym)
                    formula_first |= self.get_first(first_sym)
            else:
                # The first symbol is not an upper character, which means it is an terminal symbol.
                # In this case, we directory store the symbol into array.
                first.add(first_sym)
                formula_first.add(first_sym)
            # Insert formula's FIRST(a) into the dict.
            try:
                self.first_dict[(non_t, formula)] |= formula_first
            except KeyError:
                # The first_dict corresponding to this formula is not set before.
                self.first_dict[(non_t, formula)] = formula_first
        return first

    def append_first(self, non_t):
        """
        An add-on to get_first, focus in dealing with left-recursive grammar.

        :param non_t: str, non-terminal symbol.
        """
        for formula in self.get_all_formulas(non_t):
            first_sym = formula.split(" ")[0]
            if first_sym.isupper() and first_sym == non_t:
                self.first_dict[(non_t, formula)] |= self.get_first(first_sym)

    def get_follow(self, non_t, start_symbol='S'):
        """
        Get a non-terminal symbols' all FOLLOW(A) array.
        Insert every non-terminals' FOLLOW(A) array into follow_dict in the same time.
        Noted that this follow set only considers 'Ab' or 'AB' situation,
        in which b is add to follow(A) and first(B) is add to follow(A).

        :param non_t: str, non-terminal symbol.
        :param start_symbol: str, the start symbol of the grammar.
        :return: The non-terminal symbol's all FOLLOW(a) array.
        """
        follow = set()
        for non_terminal in self.non_ts:
            for formula in self.get_all_formulas(non_terminal):
                formula_list = formula.split(" ")
                if non_t in formula_list:
                    # The specified non-terminal symbol is in formula, then get the index of the symbol.
                    index = formula_list.index(non_t)
                    if not index == len(formula_list) - 1:
                        if formula_list[index + 1].isupper():
                            # If the follow of the symbol is an non-terminal-symbol,
                            # add the follow symbol's FIRST(A) to its follow set.
                            follow |= self.get_first(formula_list[index + 1])
                        else:
                            # If the follow of the symbol is an terminal-symbol,
                            # directory add that symbol to its FOLLOW set.
                            follow.add(formula_list[index + 1])
        follow -= {'e'}
        if non_t == start_symbol:
            follow.add('#')
        self.follow_dict[non_t] = follow
        return follow

    def append_follow(self, non_t):
        """
        An add-on to get_follow, focus on two situation: 'B->...A', and 'B->...AC, C->e',
        in which follow(B) is add to follow(A).

        :param non_t: str, non_terminal symbol.
        """
        for non_terminal in self.non_ts:
            for formula in self.get_all_formulas(non_terminal):
                formula_list = formula.split(" ")
                if non_t in formula_list:
                    index = formula_list.index(non_t)
                    if index == len(formula_list) - 1:
                        if not non_t == non_terminal:
                            # If the symbol is in the end of the formula,
                            # then add all FOLLOW(A) to the symbol's FOLLOW set.
                            try:
                                self.follow_dict[non_t] |= self.follow_dict[non_terminal]
                            except KeyError:
                                continue
                    elif formula_list[index + 1].isupper():
                        if 'e' in list(self.get_all_formulas(formula_list[index + 1])) \
                                and index == len(formula_list) - 2:
                            # If the follow of the symbol is the end of the formula and can be inferred to empty,
                            # add the formula's corresponding non-terminal symbol's FOLLOW()
                            # to the symbol's FOLLOW set.
                            try:
                                self.follow_dict[non_t] |= self.follow_dict[non_terminal]
                            except KeyError:
                                continue

    def construct_map(self):
        """
        Construct LL(1) analysis sheet and write into a csv file.
        """
        # Gather all terminal symbol that would appear in a valid sentence.
        all_terminal = set()
        for first in self.first_dict.values():
            all_terminal |= first
        for follow in self.follow_dict.values():
            all_terminal |= follow
        all_terminal -= {'e'}
        all_terminal = list(sorted(all_terminal))

        # Set the first row of analysis sheet (in python list form)
        an_matrix = [["non-t"] + all_terminal]
        for non_t in self.non_ts:
            # Initialize every non-terminal symbol's sheet row with all items filled with None.
            row = [None] * len(all_terminal)
            for formula in self.get_all_formulas(non_t):
                if formula == 'e':
                    # If the formula leads to empty, add this formula to all terminal-symbols in FOLLOW(A).
                    for single_follow in self.follow_dict[non_t]:
                        row[all_terminal.index(single_follow)] = formula
                else:
                    # Add this formula to all terminal-symbols in FIRST(formula).
                    for single_first in self.first_dict[(non_t, formula)]:
                        row[all_terminal.index(single_first)] = formula
            an_matrix.append([non_t] + row)

        # Write analysis sheet into csv file, using pandas.
        an_df = pd.DataFrame(an_matrix[1:], columns=an_matrix[0])
        an_df = an_df.set_index(["non-t"])
        print("====Analysis sheet detail====")
        print(an_df)
        print()
        an_df.to_csv(os.path.join("data", "an_map.csv"), sep='`')

    def print_grammar(self):
        """
        Print out grammar formulas.
        """
        print("====Grammar details====")
        for non_t in self.non_ts:
            formulas = self.get_all_formulas(non_t)
            print("{0:2}-> {1:}".format(non_t, "|".join(list(formulas))))
        print()


if __name__ == "__main__":
    map_construct = AnMapConstruct(init_grammar(os.path.join("OperatorPriority", "data", "grammar.txt"), "txt_file"))
    map_construct.print_grammar()
    map_construct.construct_first()
    map_construct.construct_follow('E')
