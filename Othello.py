import sys;args = sys.argv[1:]
# Nicholas Bonanno, pd. 6
import random

def GenGlobals():
    global constraints_column, constraints_row, constraints_diagonal, constraint_lut
    constraints_column = []
    constraints_row = []
    constraints_diagonal = []
    constraint_lut = [[] for i in range(64)]#each arr is formatted as [row_ind, column_ind, diag1_ind, diag2_ind]

    for i in range(8):
        constraints_row.append(z := list(i * 8 + j for j in range(8)))
        for j in z:
            constraint_lut[j].append(len(constraints_row) - 1)

    for i in range(8):
        constraints_column.append(z := list(j * 8 + i for j in range(8)))
        for j in z:
            constraint_lut[j].append(len(constraints_column) - 1)

    #generate both sets of diagonals, slopes of 1 and -1
    for i in range(1, 9):
        diagonal = []
        pos = i - 1
        for j in range(i):
            diagonal.append(pos)
            pos += 7
        constraints_diagonal.append(diagonal)
        for j in diagonal:
            constraint_lut[j].append(len(constraints_diagonal) - 1)
    for n, i in enumerate(constraints_column[len(constraints_column) - 1][1:]):
        n += 1
        diagonal = []
        pos = i
        for j in range(8 - n):
            diagonal.append(pos)
            pos += 7
        constraints_diagonal.append(diagonal)
        for j in diagonal:
            constraint_lut[j].append(len(constraints_diagonal) - 1)

    for n,i in enumerate(constraints_column[0]):
        diagonal = []
        pos = i
        for j in range(8 - n):
            diagonal.append(pos)
            pos += 9
        constraints_diagonal.append(diagonal)
        for j in diagonal:
            constraint_lut[j].append(len(constraints_diagonal) - 1)
    for n,i in enumerate(constraints_row[0][1:]):
        diagonal = []
        pos = i
        for j in range(8 - (n + 1)):
            diagonal.append(pos)
            pos += 9
        constraints_diagonal.append(diagonal)
        for j in diagonal:
            constraint_lut[j].append(len(constraints_diagonal) - 1)



def PrintBoard(board):
    output = ''
    for i in range(8):
        string = ''
        for j in board[i*8:(i + 1)*8]:
            string += f'{j}  '
        print(string)


def MarkList(pos_list, board, continue_char, ind, mark_pos, pos):
    #breakpoint()
    hit_char = False
    for i in pos_list[ind][pos_list[ind].index(pos) + 1:]:#never thought I'd wish for C macros
        if board[i] == continue_char:
            hit_char = True
            continue
        elif board[i] == '.':
            if hit_char:
                mark_pos.append(i)
            break
        else:
            break
    hit_char = False
    reverse = list(reversed(pos_list[ind]))
    for i in reverse[reverse.index(pos) + 1:]:#never thought I'd wish for C macros
        if board[i] == continue_char:
            hit_char = True
            continue
        elif board[i] == '.':
            if hit_char:
                mark_pos.append(i)
            break
        else:
            break


def MarksForX(board, pos):#pos is x pos in question
    indicies = constraint_lut[pos]
    mark_pos = []
    MarkList(constraints_row, board, 'o', indicies[0], mark_pos, pos)#rows
    MarkList(constraints_column, board, 'o', indicies[1], mark_pos, pos)#columns
    MarkList(constraints_diagonal, board, 'o', indicies[2], mark_pos, pos)#diagonals 1
    MarkList(constraints_diagonal, board, 'o', indicies[3], mark_pos, pos)#diagonals -1
    return mark_pos


def MarksForO(board, pos):#pos is x pos in question
    indicies = constraint_lut[pos]
    mark_pos = []
    MarkList(constraints_row, board, 'x', indicies[0], mark_pos, pos)#rows
    MarkList(constraints_column, board, 'x', indicies[1], mark_pos, pos)#columns
    MarkList(constraints_diagonal, board, 'x', indicies[2], mark_pos, pos)#diagonals 1
    MarkList(constraints_diagonal, board, 'x', indicies[3], mark_pos, pos)#diagonals -1
    return mark_pos


def MarkMoves(board, token):#could be improved by doing the board in a linear pass instead of for each piece, could change MarksForX and MarksForO to do that
    mark_pos = []
    if token == 'x':
        for n, i in enumerate(board):
            if i == 'x':#check all moves coming off of this
                mark_pos.extend(MarksForX(board, n))
    else: #token is o
        for n, i in enumerate(board):
            if i == 'o':#check all moves coming off of this
                mark_pos.extend(MarksForO(board, n))
    ret_board = list(board)
    #breakpoint()
    for i in mark_pos:
        ret_board[i] = '*'
    return ''.join(ret_board), set(mark_pos)


def GetDefaultToken(board):#I assume the toke indicates which side moves this time
    x_count = board.count('x')
    y_count = board.count('o')
    if 0 == x_count == y_count:
        return 'x'
    return 'x' if y_count >= x_count else 'o'

def main():
    GenGlobals()
    if len(args) == 2:
        board = args[0].lower()
        token = args[1].lower()
    elif len(args) == 1:
        if len(args[0]) == 64:
            board = args[0].lower()
            token = GetDefaultToken(board)
        else:
            board = '.'*27 + "ox......xo" + '.'*27
            token = args[0].lower()
    else:
        board = '.'*27 + "ox......xo" + '.'*27
        token = GetDefaultToken(board)


    temp = MarkMoves(board, token)
    #PrintBoard(temp[0])
    if temp[1].__len__() > 0:
        print('{' + f"{str(temp[1]).replace('[', '').replace(']', '')}" + '}')
    else:
        print('No moves possible')

if __name__ == '__main__':
    main()
