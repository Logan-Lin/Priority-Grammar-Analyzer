from OperatorPriority import FormMatrix as OFM
from SimplePriority import FormMatrix as SFM
from OperatorPriority import OperatorPriorityAn as OPA
from SimplePriority import SimplePriorityAn as SPA
from utils import init_grammar
import os


def main_menu():
    while True:
        print("\n====选择文法种类====")
        print("1-简单优先分析")
        print("2-算符优先分析")
        print("0-退出")

        try:
            choice = int(input("选择功能："))
        except ValueError:
            continue

        if choice == 0:
            exit(0)
        elif choice == 1 or choice == 2:
            grammar_menu(choice)


def grammar_menu(grammar_type):
    if grammar_type == 1:
        grammar = init_grammar(os.path.join("SimplePriority", "data", "grammar.txt"), "txt_file")
        form_matrix = SFM.FormMatrix(grammar)
    else:
        grammar = init_grammar(os.path.join("OperatorPriority", "data", "grammar.txt"), "txt_file")
        form_matrix = OFM.FormMatrix(grammar)

    header = {1: "简单", 2:"算符"}[grammar_type]
    start_symbol = "E"
    while True:
        print("\n===={}优先分析====".format(header))
        print("1-输入/查看文法")
        print("2-开始分析")
        print("3-显示分析矩阵")
        print("0-返回上一级")

        try:
            choice = int(input("选择功能："))
        except ValueError:
            continue

        if choice == 0:
            return
        elif choice == 1:
            form_matrix.print_grammar()
            print("开始符号：{}".format(start_symbol))
            print("输入新的文法，格式:A->a|b c，注意用空格将产生式中的符号隔开。")
            print("输入空行结束，什么都不输入按下回车则不更改文法。")
            print("文法第一条产生式的非终结符号将作为文法的开始符号。")

            line_count = 0
            lines = []
            while True:
                line = input("{}-".format(line_count + 1))
                if len(line) == 0:
                    break
                lines.append(line)
                line_count += 1
            if line_count == 0:
                continue

            start_symbol = lines[0].split("->")[0]
            grammar = init_grammar(lines, "text")
            if grammar_type == 1:
                form_matrix = SFM.FormMatrix(grammar)
            else:
                form_matrix = OFM.FormMatrix(grammar)
        elif choice == 2:
            print("输入需要分析的输入串，格式类似'i + i * i'，注意用空格将符号隔开。")
            input_line = input()
            if len(input_line) > 0:
                if grammar_type == 1:
                    grammar_an = SPA.SimplePriority(grammar)
                else:
                    grammar_an = OPA.OperatorPriorityAn(grammar)
                grammar_an.scan_series(start_symbol, input_line.split(" "))
        elif choice == 3:
            if grammar_type == 1:
                form_matrix.print_relation_matrix(form_matrix.relation_matrix, "Relation")
            else:
                form_matrix.print_priority(form_matrix.priority_matrix, "relationship")
                form_matrix.print_matrix(form_matrix.floyd_matrix, "floyd",
                                         columns=form_matrix.ts, index=form_matrix.floyd_index)


if __name__ == "__main__":
    main_menu()
