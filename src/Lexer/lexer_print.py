from typing import Any
from Lexer.lexer_consts import *

def print_table(table: list[list[Any]] | list[tuple[Any]]):
    if len(table) == 0:    return
    if len(table[0]) == 0: return

    max_size: list[int] = list(0 for j in range(len(table[0])))

    for i in range(len(table)):
        for j in range(len(table[0])):
            max_size[j] = max(max_size[j], len(str(table[i][j])))

    for i in range(len(max_size)):
        max_size[i] = max_size[i] + 2

    # --------------------------------
    def print_upper(sizes: list[int]):
        print('╭', end='')
        for i in range(len(sizes) - 1):
            print('─' * sizes[i], end='')
            print('┬', end='')
        print('─' * sizes[len(sizes) - 1], end='')
        print('╮')

    def print_middle(sizes: list[int]):
        print('├', end='')
        for i in range(len(sizes) - 1):
            print('─' * sizes[i], end='')
            print('┼', end='')
        print('─' * sizes[len(sizes) - 1], end='')
        print('┤')

    def print_down(sizes: list[int]):
        print('╰', end='')
        for i in range(len(sizes) - 1):
            print('─' * sizes[i], end='')
            print('┴', end='')
        print('─' * sizes[len(sizes) - 1], end='')
        print('╯')

    def print_row(sizes: list[int], row: list[Any] | tuple[Any]):
        print('│', end='')
        for i in range(len(sizes) - 1):
            print(str(row[i]).center(sizes[i]), end='')
            print('│', end='')
        print(str(row[len(sizes) - 1]).center(sizes[len(sizes) - 1]), end='')
        print('│')
    # --------------------------------
    print_upper(max_size)
    for i in range(len(table) - 1):
        print_row(max_size, table[i])
        print_middle(max_size)
    print_row(max_size, table[len(table) - 1])
    print_down(max_size)


def print_console(message: str, message_type: CONSOLE_COLORS = CONSOLE_COLORS.NORMAL):
    print(message_type.value + message + CONSOLE_COLORS.NORMAL.value)