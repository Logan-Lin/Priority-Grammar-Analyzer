import pandas as pd
import numpy as np
import time


class FormMatrix:
    def __init__(self, grammar):
        self.grammar = grammar
        self.non_ts = list(sorted(grammar[~grammar.index.duplicated(keep='first')].index))
        self.floyd_index = ["f", "g"]

        self.ts = self.gather_all_terminal()
        self.ts.append("#")
        self.ts_count = len(self.ts)
        self.non_ts_count = len(self.non_ts)

        # self.print_grammar()

        equal_matrix = self.cal_equal()
        # self.print_matrix(equal_matrix, "equal")

        first_matrix = self.cal_matrix("firstvt")
        # self.print_matrix(first_matrix, "firstvt", columns=self.ts, index=self.non_ts)
        last_matrix = self.cal_matrix("lastvt")
        # self.print_matrix(last_matrix, "lastvt", columns=self.ts, index=self.non_ts)

        self.priority_matrix = self.construct_priority_matrix(first_matrix, last_matrix, equal_matrix)
        # self.print_priority(self.priority_matrix, "relationship")

        self.floyd_matrix = self.cal_floyd()
        # self.print_matrix(self.floyd_matrix, "floyd", columns=self.ts, index=self.floyd_index)

    def print_grammar(self):
        """
        Print out grammar formulas.
        """
        print("====Grammar details====")
        for non_t in self.non_ts:
            formulas = self.get_all_formulas(non_t)
            print("{0:2}-> {1:}".format(non_t, "|".join(list(formulas))))
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

    def gather_all_terminal(self):
        """
        Gather all terminal symbol from grammar.
        """
        result = set()
        for non_t in self.non_ts:
            for formula in self.get_all_formulas(non_t):
                for char in formula.split(" "):
                    if not char.isupper():
                        result.add(char)
        return list(sorted(result))

    def print_matrix(self, matrix, name, columns=None, index=None):
        if columns is None:
            columns = self.ts
        if index is None:
            index = self.ts
        df = pd.DataFrame(matrix, columns=columns, index=index)
        print("===={} matrix====".format(name))
        print(df)
        print()

    def print_priority(self, matrix, name):
        priority_df = pd.DataFrame(matrix, columns=self.ts, index=self.ts).applymap(
            lambda x: {0: "-", 1: ">", 2: "=", -1: "<", 3: "A"}[x])
        print("===={} matrix====".format(name))
        print(priority_df)
        print()

    def cal_equal(self):
        """
        Calculate equal matrix.

        :return: numpy array, containing equal matrix.
        """
        result = np.zeros((self.ts_count, self.ts_count), int)
        for non_t in self.non_ts:
            for formula in self.get_all_formulas(non_t):
                chars = formula.split(" ")
                for i in range(len(chars) - 2):
                    if not chars[i].isupper() and not chars[i + 2].isupper():
                        # '..aUb..' like formula.
                        result[self.ts.index(chars[i]), self.ts.index(chars[i + 2])] = 1
                for i in range(len(chars) - 1):
                    if not chars[i].isupper() and not chars[i + 1].isupper():
                        # '..ab..' like formula.
                        result[self.ts.index(chars[i]), self.ts.index(chars[i + 1])] = 1
        return result

    def get_non_t(self, non_t, matrix="firstvt"):
        """
        Get non-terminal symbol V with condition like U->V... or U->...V.

        :param non_t: str, non-terminal symbol.
        :param matrix: str, set to "firstvt" or "lastvt" to distinguish two formula types.
        :return: list, containing all non-terminal symbols which matches condition.
        """
        index = {"firstvt": 0, "lastvt": -1}[matrix]
        result = []
        for non_terminal in self.non_ts:
            for formula in self.get_all_formulas(non_terminal):
                if formula.split(" ")[index] == non_t:
                    result.append(non_terminal)
        return result

    def cal_matrix(self, matrix="firstvt"):
        """
        Calculate firstvt or lastvt matrix.

        :param matrix: str, set to "fristvt" or "lastvt" to distinguish two matrix types.
        :return: numpy array, containing result matrix.
        """
        # Initialise matrix.
        result = np.zeros((self.non_ts_count, self.ts_count), int)
        index = {"firstvt": [0, 1], "lastvt": [-1, -2]}[matrix]
        stack = []
        for non_t in self.non_ts:
            for formula in self.get_all_formulas(non_t):
                chars = formula.split(" ")
                if chars[index[0]].isupper() and len(chars) >= 2:
                    result[self.non_ts.index(non_t), self.ts.index(chars[index[1]])] = 1
                    stack.append((non_t, chars[index[1]]))
                if not chars[index[0]].isupper():
                    result[self.non_ts.index(non_t), self.ts.index(chars[index[0]])] = 1
                    stack.append((non_t, chars[index[0]]))

        # print("===={} matrix constructing stack====".format(matrix))
        while len(stack) > 0:
            # print(stack)
            top = stack[-1]
            del stack[-1]
            for non_t in self.get_non_t(top[0], matrix=matrix):
                if result[self.non_ts.index(non_t), self.ts.index(top[1])] == 0:
                    result[self.non_ts.index(non_t), self.ts.index(top[1])] = 1
                    stack.append((non_t, top[1]))
        return result

    def construct_priority_matrix(self, firstvt, lastvt, equal):
        """
        Construct operator priority matrix.

        :param firstvt: numpy array, firstvt matrix.
        :param lastvt: numpy array, lastvt matrix.
        :param equal: numpy array, equal matrix.
        :return: numpy array, containing operator priority matrix.
        """
        result = 2 * equal.copy()
        result_prior = np.zeros((self.ts_count, self.ts_count))
        result_lower = np.zeros((self.ts_count, self.ts_count))

        for non_t in self.non_ts:
            for formula in self.get_all_formulas(non_t):
                chars = formula.split(" ")
                for i in range(len(chars)):
                    if not chars[i].isupper():
                        if not i == 0 and chars[i - 1].isupper():
                            # Ub format, chars[i-1] is U, chars[i] is b.
                            result_prior[lastvt[self.non_ts.index(chars[i - 1]), :] == 1, self.ts.index(chars[i])] = 1
                            result_prior[lastvt[self.non_ts.index(chars[i - 1]), :] == 1, self.ts.index("#")] = 1
                        if not i == len(chars) - 1 and chars[i + 1].isupper():
                            # aU format, chars[i] is a, chars[i+1] is U.
                            result_lower[self.ts.index(chars[i]), firstvt[self.non_ts.index(chars[i + 1]), :] == 1] = -1
                            result_lower[self.ts.index("#"), firstvt[self.non_ts.index(chars[i + 1]), :] == 1] = -1
        # self.print_priority(result_prior, "prior")
        # self.print_priority(result_lower, "lower")

        # Check if there are any two symbols that have two relationships.
        if True in ((result_lower == -1) * (result_prior == 1)):
            raise ValueError("Grammar is not a valid operator priority grammar!")
        result = result + result_prior + result_lower
        result[-1, -1] = 3
        return result

    def get_relation(self, s1, s2):
        """
        Get the relation between symbol s1 and symbol s2.

        :param s1: The first symbol to be compared.
        :param s2: The second symbol to be compared.
        :return: int, the relationship between s1 and s2.
            0 means s1 = s2, -1 means s1 < s2, 1 means s1 > s2.
        :raise ValueError: When there is no relationship between s1 and s2.
        """
        result = self.priority_matrix[self.ts.index(s1), self.ts.index(s2)]
        if result == 2:
            result = 0
        elif result == 0:
            raise ValueError("No relationship between {} and {}.".format(s1, s2))
        return result

    def cal_floyd(self):
        """
        Flatten relationship matrix using Floyd method.

        :return: numpy array, containing Floyd result matrix.
        """
        result = np.ones((2, self.ts_count), int)
        start = time.time()
        while True:
            changed = False
            for t1 in self.ts:
                for t2 in self.ts:
                    try:
                        relation = self.get_relation(t1, t2)
                    except ValueError:
                        continue
                    f1 = result[self.floyd_index.index("f"), self.ts.index(t1)]
                    g2 = result[self.floyd_index.index("g"), self.ts.index(t2)]
                    if relation == 1 and f1 <= g2:
                        result[0, self.ts.index(t1)] = result[1, self.ts.index(t2)] + 1
                        changed = True
                    if relation == -1 and f1 >= g2:
                        result[1, self.ts.index(t2)] = result[0, self.ts.index(t1)] + 1
                        changed = True
                    if relation == 0 and not f1 == g2:
                        max_value = max(f1, g2)
                        result[0, self.ts.index(t1)] = max_value
                        result[1, self.ts.index(t2)] = max_value
                        changed = True
            if not changed:
                break
            if time.time() - start > 2:
                raise ValueError("Some error in grammar causing floyd calculation timeout.")
        return result

