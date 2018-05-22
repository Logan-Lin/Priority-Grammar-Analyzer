import pandas as pd
import os

from SimplePriority.FormMatrix import FormMatrix
from utils import init_grammar


class SimplePriority:
    def __init__(self, grammar):
        self.grammar = grammar
        self.form_matrix = FormMatrix(grammar)

        self.symbols = self.form_matrix.symbols
        self.relation_matrix = self.form_matrix.relation_matrix

    def get_priority(self, first, second):
        """
        Get the priority relationship between first and second identifiers.
        :param first: str, the first identifier.
        :param second: str, the second identifier.
        :return: -1, 0 or 1, means first < second, first = second and first > second.
        """
        if first == "#":
            return -1
        if second == "#":
            return 1
        relation = self.relation_matrix[self.symbols.index(first), self.symbols.index(second)]
        if relation == 2:
            relation = 0
        return relation

    def print_stack(self, stack, current):
        """
        Print stack information to console.

        :param stack: list, analysis stack.
        :param current: str, current scanning identifier.
        """
        print("[{:20}]<- {:5}{}{}{}".format(
            " ".join(stack), current, stack[-1], {0: "=", 1: ">", -1: "<"}[self.get_priority(stack[-1], current)], current))

    def control(self, start_symbol, input_series):
        """
        The control function of simple priority grammar analysis.

        :param start_symbol: str, the start symbol of this grammar.
        :param input_series: list, input identifier series.
        """
        print("====Analysis process====")
        stack = ["#"]
        global scan_index
        scan_index = 0
        input_series += ["#"]

        current = input_series[scan_index]
        self.print_stack(stack, current)
        scan_index += 1

        while True:
            while not self.get_priority(stack[-1], current) == 1:
                stack.append(current)
                self.print_stack(stack, current)

                current = input_series[scan_index]
                scan_index += 1

            start_index = len(stack) - 1
            while not self.get_priority(stack[start_index - 1], stack[start_index]) == -1:
                start_index -= 1

            non_t = list(self.grammar.index[self.grammar['formula'] == " ".join(stack[start_index:])])[0]
            del stack[start_index:]
            stack.append(non_t)
            self.print_stack(stack, current)

            if non_t == start_symbol:
                if not len(stack) == 2:
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


if __name__ == "__main__":
    simple_priority = SimplePriority(init_grammar(os.path.join("data", "grammar.txt"), "txt_file"))
    simple_priority.scan_series("E", "i * ( i + i ) + ( i * i ) + i * i".split(" "))
