import pandas as pd


def process_binary(bin_str):
    """
    Turn binary string such as (20, -) into coding integer.

    :param bin_str: string, binary string output by lexical analysis, like '(20, -)'.
    :return: Extracted coding integer, like 20.
    """
    return int(bin_str[1:].split(",")[0])


def get_current_description(coding_array, scan_index, coding_df, column="secondary"):
    """
    Return current description based on current coding.

    :param column: string, Set the column to search for. Set to 'description' to search from original column.
    :param coding_array: list, the lexical coding series.
    :param scan_index: int, current scanning index of coding series.
    :param coding_df: pandas data frame, information about coding and its corresponding identifiers.
    :raise: ValueError if can't find description based on current coding
    :return: string, Description (identifier) current coding represented
    """
    coding = coding_array[scan_index]
    desc = coding_df.loc[coding][column]
    if not type(desc).__name__ == "str":
        raise ValueError("No valid identifier matching coding {}".format(coding))
    return desc


def load_coding(file_name):
    """
    Load lexical analysis's output into coding array.

    :param file_name: string, output file's directory
    :return: array, the lexical coding series.
    """
    coding_array = []
    with open(file_name, "r") as file:
        for row in file.readlines():
            if len(row) > 2:
                # If the row is not empty
                row_coding = list(map(process_binary, row.split(")")[:-1]))
                coding_array += row_coding
    # Append the end symbol to the end of coding series.
    coding_array.append(52)
    return coding_array


def init_grammar(file, method="csv_file"):
    """
    Create grammar data frame using different inputs.

    :param file: file directory or string list, based on what method to use. If method is "csv_file",
        'file' should be file directory of grammar csv file; if method is "txt_file",
        'file' should be file directory of grammar plain text file; if method is "text",
        'file' should be string list with every line contains one grammar formula.
    :param method: str, used to distinguish three different grammar initialization methods.
        Can be 'csv_file', 'txt_file' or 'text'.
    :return: pandas data frame, containing grammar details.
    """
    if method == "csv_file":
        return pd.read_csv(file, delimiter='`', index_col=0)
    index = []
    grammar_matrix = []
    if method == "txt_file":
        with open(file, "r") as txt_file:
            for line in txt_file.read().splitlines():
                if len(line) == 2:
                    continue
                non_t, formulas = line.split("->")
                non_t = non_t.strip()
                for formula in formulas.split('|'):
                    formula = formula.strip()
                    index.append(non_t)
                    grammar_matrix.append(formula)
    elif method == "text":
        for line in file:
            non_t, formulas = line.split("->")
            for formula in formulas.split('|'):
                index.append(non_t)
                grammar_matrix.append(formula)
    return pd.DataFrame(grammar_matrix, index=index, columns=["formula"])
