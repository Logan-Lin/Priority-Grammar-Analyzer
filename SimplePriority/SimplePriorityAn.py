import pandas as pd
import os

import sys

sys.path.append(os.path.join("..", ""))

from SimplePriority import FormMatrix

coding_df = pd.read_csv(os.path.join("..", "coding.csv"), delimiter=' ', index_col=0)
symbols = FormMatrix.symbols
relation_matrix = FormMatrix.relation_matrix
grammar = FormMatrix.grammar


def get_priority(first, second):
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
    relation = relation_matrix[symbols.index(first), symbols.index(second)]
    if relation == 2:
        relation = 0
    return relation


def print_stack(stack, current):
    """
    Print stack information to console.

    :param stack: list, analysis stack.
    :param current: str, current scanning identifier.
    """
    print("[{:20}]<- {:5}{}{}{}".format(
        " ".join(stack), current, stack[-1], {0: "=", 1: ">", -1: "<"}[get_priority(stack[-1], current)], current))


def control(start_symbol, input_series):
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
    print_stack(stack, current)
    scan_index += 1

    while True:
        while not get_priority(stack[-1], current) == 1:
            stack.append(current)
            print_stack(stack, current)

            current = input_series[scan_index]
            scan_index += 1

        start_index = len(stack) - 1
        while not get_priority(stack[start_index - 1], stack[start_index]) == -1:
            start_index -= 1

        non_t = list(grammar.index[grammar['formula'] == " ".join(stack[start_index:])])[0]
        del stack[start_index:]
        stack.append(non_t)
        print_stack(stack, current)

        if non_t == start_symbol:
            if not len(stack) == 2:
                continue
            return


def scan_series(start_symbol, series):
    """
    Scan on input series.

    :param series: list, containing input identifier series.
    :param start_symbol: str, the start symbol of grammar.
    """
    try:
        control(start_symbol, series)
        print("Input series '{}' valid!".format(" ".join(series[:-1])))
    except (KeyError, ValueError, IndexError) as e:
        print("Error at position {}. {}".format(scan_index + 1, e))


if __name__ == "__main__":
    scan_series("E", "i * ( i + i ) + ( i * i ) + i * i".split(" "))
