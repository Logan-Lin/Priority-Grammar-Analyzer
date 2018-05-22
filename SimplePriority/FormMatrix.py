import numpy as np
import pandas as pd


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


class FormMatrix:
    def __init__(self, grammar):
        self.grammar = grammar
        self.non_ts = grammar[~grammar.index.duplicated(keep='first')].index
        self.print_grammar()

        # Calculate LEAD, LAST and EQUAL matrix.
        self.symbols = self.gather_all_symbols()
        self.symbol_count = len(self.symbols)
        self.lead_matrix = self.cal_matrix("lead")
        self.last_matrix = self.cal_matrix("last")
        self.equal_matrix = self.cal_equal()

        # Calculate < (lower) and > (prior) matrix.
        self.lower_matrix = np.dot(self.equal_matrix, self.lead_matrix)
        self.lead_matrix_s = self.lead_matrix.copy()
        np.fill_diagonal(self.lead_matrix_s, 1)
        self.prior_matrix = self.last_matrix.T.dot(self.equal_matrix).dot(self.lead_matrix_s)
        for non_t in self.non_ts:
            self.prior_matrix[:, self.symbols.index(non_t)] = 0
            self.print_matrix(self.lower_matrix, "lower")
        self.print_matrix(self.prior_matrix, "prior")

        # In relation matrix, 0 means N/A, 1 means prior, -1 means lower, 2 means equal.
        # relation_df is a more intuitive version, but not suitable for grammar analyzer.
        self.relation_matrix = 2 * self.equal_matrix - self.lower_matrix + self.prior_matrix
        print("====Relation matrix====")
        relation_df = pd.DataFrame(self.relation_matrix, columns=self.symbols, index=self.symbols).applymap(
            lambda x: {0: "-", 1: ">", 2: "=", -1: "<"}[x])
        print(relation_df)

    def print_grammar(self):
        """
        Print out grammar formulas.
        """
        print("====Grammar details====")
        for non_t in self.non_ts:
            formulas = self.get_all_formulas(non_t)
            print("{0:2}-> {1:}".format(non_t, "|".join(list(formulas))))
        print()

    def print_matrix(self, matrix, name):
        df = pd.DataFrame(matrix, columns=self.symbols, index=self.symbols)
        print("===={} matrix====".format(name))
        print(df)
        print()

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

    def gather_all_symbols(self):
        """
        Gather all symbol from grammar.
        """
        result = set()
        for non_t in self.non_ts:
            result.add(non_t)
            for formula in self.get_all_formulas(non_t):
                result |= set(formula.split(" "))
        return list(sorted(result))

    def cal_matrix(self, matrix="lead"):
        """
        Calculate the grammar's LEAD or LAST matrix. Output the result at the same time.

        :param matrix: str, set to "lead" to calculate LEAD matrix, to "last" to calculate LAST matrix.
        :return: numpy array, containing LEAD or LAST matrix.
        """
        result = np.zeros((self.symbol_count, self.symbol_count), int)
        index = {"lead": 0, "last": -1}[matrix]
        for non_t in self.non_ts:
            for formula in self.get_all_formulas(non_t):
                result[self.symbols.index(non_t), self.symbols.index(formula.split(" ")[index])] = 1

        result_plus = result.copy()
        for i in range(0, result.shape[0]):
            for j in range(0, result.shape[0]):
                if result_plus[j, i] == 1:
                    for k in range(0, result.shape[0]):
                        result_plus[j, k] = result_plus[j, k] + result_plus[i, k]
        print()
        result_plus = np.where(result_plus.copy() > 0, 1, result_plus)
        self.print_matrix(result_plus, "{}+".format(matrix))
        return result_plus

    def cal_equal(self):
        """
        Calculate equal matrix.

        :return: numpy array, containing EQUAL matrix.
        """
        result = np.zeros((self.symbol_count, self.symbol_count), int)
        for non_t in self.non_ts:
            for formula in self.get_all_formulas(non_t):
                chars = formula.split(" ")
                for i in range(len(chars) - 1):
                    result[self.symbols.index(chars[i]), self.symbols.index(chars[i + 1])] = 1
                self.print_matrix(result, "equal")
        return result
