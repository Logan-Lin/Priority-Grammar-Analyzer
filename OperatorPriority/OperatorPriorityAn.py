import os

import sys

sys.path.append(os.path.join("..", ""))

from OperatorPriority.FormMatrix import FormMatrix
from utils import init_grammar


def get_terminal_index(formula):
    """
    Get all indexes of terminal symbol in a formula.

    :param formula: str, the formula to be searched.
    :return: set, containing all index number of terminal symbol in given formula.
    """
    result = set()
    formula_list = formula.split(" ")
    for i in range(len(formula_list)):
        if not formula_list[i].isupper():
            result.add(i)
    return result


class OperatorPriorityAn:
    def __init__(self, grammar):
        self.form_matrix = FormMatrix(grammar)

        self.ts = self.form_matrix.ts
        self.non_ts = self.form_matrix.non_ts

        self.floyd_matrix = self.form_matrix.floyd_matrix
        self.floyd_index = self.form_matrix.floyd_index

        self.grammar = self.form_matrix.grammar

    def get_priority(self, first, second):
        """
        Get the priority relationship between first and second identifiers.
        :param first: str, the first identifier.
        :param second: str, the second identifier.
        :return: -1, 0 or 1, means first < second, first = second and first > second.
        """
        f1 = self.floyd_matrix[self.floyd_index.index("f"), self.ts.index(first)]
        g2 = self.floyd_matrix[self.floyd_index.index("g"), self.ts.index(second)]
        if f1 > g2:
            return 1
        if f1 == g2:
            return 0
        if f1 < g2:
            return -1

    def print_stack(self, stack, current, formulas=None):
        """
        Print stack information to console.

        :param stack: list, analysis stack.
        :param current: str, current scanning identifier.
        :param formulas: list, leftmost phrase to be replace,
            or chosen non-terminal symbol to be push into stack.
        """
        if formulas is None:
            formulas = []
        if stack[-1].isupper():
            top = stack[-2]
        else:
            top = stack[-1]
        print("[{:20}]<- {:5}{:2}{:2}{:4}{}".format(
            " ".join(stack), current, top, {0: "=", 1: ">", -1: "<"}[self.get_priority(top, current)], current,
            " -> ".join(formulas)))

    def get_non_t(self, replacing_formula):
        """
        Look for corresponding non-terminal symbol based on
        all operator (terminal symbol) in given formula.

        :param replacing_formula: str, the formula to be replaced into non-terminal symbol.
        :return: tuple (str, str), the corresponding non-terminal symbol and the found matching formula.
        :raise: KeyError when it is unable to find corresponding non-terminal symbol.
        """
        t_in_formula = set()
        for char in replacing_formula.split(" "):
            if not char.isupper():
                t_in_formula.add(char)
        for non_t in self.non_ts:
            for formula in self.form_matrix.get_all_formulas(non_t):
                try:
                    # Make sure that the formula contains operator we want to replace.
                    if not t_in_formula.issubset(formula.split(" ")):
                        raise ValueError
                    # Make sure that all operator are matched in place.
                    for index in get_terminal_index(replacing_formula):
                        if not replacing_formula.split(" ")[index] == formula.split(" ")[index]:
                            raise ValueError
                except ValueError:
                    continue
                return non_t, formula
        raise KeyError("No matching formula for operator {}".format(" ".join(t_in_formula)))

    def control(self, start_symbol, input_series):
        """
        The control function of operator priority analyzer.

        :param start_symbol: str, start symbol of function.
        :param input_series: list, input identifier series.
        """
        print("====Analysis Process====")
        stack = ["#"]
        input_series.append("#")

        global scan_index
        scan_index = 0

        current = input_series[scan_index]
        scan_index += 1
        self.print_stack(stack, current)

        while True:
            while True:
                if stack[-1].isupper():
                    top = stack[-2]
                else:
                    top = stack[-1]
                if self.get_priority(top, current) == 1:
                    break

                stack.append(current)
                current = input_series[scan_index]
                self.print_stack(stack, current)
                scan_index += 1

            start_index = len(stack) - 1
            while True:
                if stack[start_index].isupper():
                    start_index -= 1
                right = stack[start_index]
                start_index -= 1
                if stack[start_index].isupper():
                    start_index -= 1

                if self.get_priority(stack[start_index], right) == -1:
                    break

            formula = " ".join(stack[start_index + 1:])
            non_t, choose_formula = self.get_non_t(formula)
            del stack[start_index + 1:]
            stack.append(non_t)

            formulas = [choose_formula, non_t]
            if not formula == choose_formula:
                formulas.insert(0, formula)
            self.print_stack(stack, current, formulas)

            if non_t == start_symbol:
                if not len(stack) == 2 or not scan_index == len(input_series):
                    continue
                return

    def scan_series(self, start_symbol, series):
        """
        Scan on input series.

        :param series: list, containing input identifier series.
        :param start_symbol: str, the start symbol of grammar.
        """
        try:
            self.control(start_symbol, series)
            print("Input series '{}' valid!".format(" ".join(series[:-1])))
        except (KeyError, ValueError, IndexError) as e:
            print("Error at position {}. {}".format(scan_index + 1, e))
        print()


if __name__ == "__main__":
    an = OperatorPriorityAn(init_grammar(os.path.join("data", "grammar.txt"), "txt_file"))
    an.scan_series("E", "i + i".split(" "))
