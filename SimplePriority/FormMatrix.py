import pandas as pd
import numpy as np
import os

from utils import init_grammar


grammar = init_grammar(os.path.join("data", "Grammar.csv"), "csv_file")
non_ts = grammar[~grammar.index.duplicated(keep='first')].index


def print_grammar():
    """
    Print out grammar formulas.
    """
    print("====Grammar details====")
    for non_t in non_ts:
        formulas = get_all_formulas(non_t)
        print("{0:2}-> {1:}".format(non_t, "|".join(list(formulas))))
    print()


def print_matrix(matrix, name):
    df = pd.DataFrame(matrix, columns=symbols, index=symbols)
    print("===={} matrix====".format(name))
    print(df)
    print()


def get_all_formulas(non_t):
    """
    Returns all formulas corresponding to the specified non-terminal symbol.

    :param non_t: string, the non-terminal symbol.
    :return: list or pandas Series, all formulas corresponding to the specified non-terminal symbol
    """
    formulas = grammar.loc[non_t]
    formulas = formulas["formula"]
    if type(formulas).__name__ == "str":
        # If there is only one formula corresponding to the non-terminal symbol,
        # the returned 'formulas' could be string object.
        # Considering we have to traverse 'formulas', we turn it to a list here.
        formulas = [formulas]
    return formulas


def gather_all_symbols():
    """
    Gather all symbol from grammar.
    """
    result = set()
    for non_t in non_ts:
        result.add(non_t)
        for formula in get_all_formulas(non_t):
            result |= set(formula.split(" "))
    return list(sorted(result))


def cal_matrix_pow(matrix, n):
    """
    Calculate the result of n times matrix multiply,
    in other words, matrix * matrix * ... * matrix.

    :param matrix: numpy array
    :param n: the time of multiply
    :return: numpy array, the calculation result.
    """
    result = matrix.copy()
    for i in range(n):
        result = result.dot(matrix)
    return result


def cal_matrix(matrix="lead"):
    """
    Calculate the grammar's LEAD or LAST matrix. Output the result at the same time.

    :param matrix: str, set to "lead" to calculate LEAD matrix, to "last" to calculate LAST matrix.
    :return: numpy array, containing LEAD or LAST matrix.
    """
    result = np.zeros((symbol_count, symbol_count), int)
    index = {"lead": 0, "last": -1}[matrix]
    for non_t in non_ts:
        for formula in get_all_formulas(non_t):
            result[symbols.index(non_t), symbols.index(formula.split(" ")[index])] = 1

    result_plus = result.copy()
    for i in range(0, result.shape[0]):
        for j in range(0, result.shape[0]):
            if result_plus[j, i] == 1:
                for k in range(0, result.shape[0]):
                    result_plus[j, k] = result_plus[j, k] + result_plus[i, k]
    print()
    result_plus = np.where(result_plus.copy() > 0, 1, result_plus)
    print_matrix(result_plus, "{}+".format(matrix))
    return result_plus


def cal_equal():
    """
    Calculate equal matrix.

    :return: numpy array, containing EQUAL matrix.
    """
    result = np.zeros((symbol_count, symbol_count), int)
    for non_t in non_ts:
        for formula in get_all_formulas(non_t):
            chars = formula.split(" ")
            for i in range(len(chars) - 1):
                result[symbols.index(chars[i]), symbols.index(chars[i + 1])] = 1
    print_matrix(result, "equal")
    return result


print_grammar()

# Calculate LEAD, LAST and EQUAL matrix.
symbols = gather_all_symbols()
symbol_count = len(symbols)
lead_matrix = cal_matrix("lead")
last_matrix = cal_matrix("last")
equal_matrix = cal_equal()

# Calculate < (lower) and > (prior) matrix.
lower_matrix = np.dot(equal_matrix, lead_matrix)
lead_matrix_s = lead_matrix.copy()
np.fill_diagonal(lead_matrix_s, 1)
prior_matrix = last_matrix.T.dot(equal_matrix).dot(lead_matrix_s)
for non_t in non_ts:
    prior_matrix[:, symbols.index(non_t)] = 0
print_matrix(lower_matrix, "lower")
print_matrix(prior_matrix, "prior")

# In relation matrix, 0 means N/A, 1 means prior, -1 means lower, 2 means equal.
# relation_df is a more intuitive version, but not suitable for grammar analyzer.
relation_matrix = 2 * equal_matrix - lower_matrix + prior_matrix
print("====Relation matrix====")
relation_df = pd.DataFrame(relation_matrix, columns=symbols, index=symbols).applymap(
    lambda x: {0: "-", 1: ">", 2: "=", -1: "<"}[x])
print(relation_df)
print()
