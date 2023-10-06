import sys;args = sys.argv[1:]
# Nicholas Bonanno, pd. 6
import random


def ReplaceStringPos(string, pos, new_string):
    return f'{string[0:pos]}{new_string}{string[pos + 1:]}'

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


def GetBoard(board):#PrintBoard but returns instead of printing
    out = ''
    for i in range(8):
        string = ''
        for j in board[i*8:(i + 1)*8]:
            string += f'{j}  '
        out += string.strip() + '\n'
    return out


def PrintBoard(board):
    for i in range(8):
        string = ''
        for j in board[i*8:(i + 1)*8]:
            string += f'{j}  '
        print(string.strip())


def MarkList(pos_list, board, continue_char, ind, mark_pos, pos):
    #breakpoint()
    hit_char = False
    for i in pos_list[ind][pos_list[ind].index(pos) + 1:]:
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


def MarksForChar(board, pos, char):#pos is x pos in question
    indicies = constraint_lut[pos]
    mark_pos = []
    continue_char = ['x', 'o'][{'x':1, 'o':0}[char]]
    MarkList(constraints_row, board, continue_char, indicies[0], mark_pos, pos)#rows
    MarkList(constraints_column, board, continue_char, indicies[1], mark_pos, pos)#columns
    MarkList(constraints_diagonal, board, continue_char, indicies[2], mark_pos, pos)#diagonals 1
    MarkList(constraints_diagonal, board, continue_char, indicies[3], mark_pos, pos)#diagonals -1
    return mark_pos


def MarksListing(board, token):#list of possible moves
    marks_pos = []
    for n, i in enumerate(board):
        if i == token:#check all moves coming off of this
            marks_pos.extend(MarksForChar(board, n, token))
    return list(set(marks_pos))


def MarkMoves(board, token):#could be improved by doing the board in a linear pass instead of for each piece, could change MarksForX and MarksForO to do that
    mark_pos = MarksListing(board,  token)

    ret_board = list(board)
    #breakpoint()
    for i in mark_pos:
        ret_board[i] = '*'
    return ''.join(ret_board), set(mark_pos)


def GetToken(board):#I assume the token indicates which side moves this time
    x_moves = MarkMoves(board, 'x')[0].count('*')
    o_moves = MarkMoves(board, 'o')[0].count('*')
    if x_moves == 0:
        return 'o'
    if o_moves == 0:
        return 'x'
    x_count = board.count('x')
    o_count = board.count('o')
    if 0 == x_count == o_count:
        return 'x'
    return 'x' if o_count >= x_count else 'o'


def ProcessArgs():
    board = '.'*27 + "ox......xo" + '.'*27
    token = None
    move = None
    if len(args) == 3:
        board = args[0].lower()
        token = args[1].lower()
        move = args[2].lower()
    if len(args) == 2:
        if args[0].__len__() == 64:
            board = args[0].lower()
        elif args[0].lower() == 'x' or args[0].lower() == 'o':
            token = args[0].lower()
        else:
            move = args[0].lower()

        if args[1].__len__() == 64:
            board = args[1].lower()
        elif args[1].lower() == 'x' or args[1].lower() == 'o':
            token = args[1].lower()
        else:
            move = args[1].lower()
    if len(args) == 1:
        if args[0].__len__() == 64:
            board = args[0].lower()
        elif args[0].lower() == 'x' or args[0].lower() == 'o':
            token = args[0].lower()
        else:
            move = args[0].lower()
    if token is None:
        token = GetToken(board).lower()
    return board, token, move


def Move(board, move, token):#plays piece and then updates the board
    board = ReplaceStringPos(board, move, token.upper())
    constraint_indx = constraint_lut[move]
    row = constraints_row[constraint_indx[0]]
    row, row2 = row[row.index(move) + 1:], reversed(row[0:row.index(move)])
    column = constraints_column[constraint_indx[1]]
    column, column2 = column[column.index(move) + 1:], reversed(column[0:column.index(move)])
    diag1 = constraints_diagonal[constraint_indx[2]]
    diag1, diag12 = diag1[diag1.index(move) + 1:], reversed(diag1[0:diag1.index(move)])
    diag2 = constraints_diagonal[constraint_indx[3]]
    diag2, diag22 = diag2[diag2.index(move) + 1:], reversed(diag2[0:diag2.index(move)])

    continue_token = ['x', 'o'][{'x':1, 'o':0}[token]]
    for constraint in [row, column, diag1, diag2, row2, column2, diag12, diag22]:
        to_set = []
        should_set = False
        for pos in constraint:
            if (c := board[pos]) == continue_token:
                to_set.append(pos)
            elif c == token:
                should_set = True
                break
            else:
                break
        if should_set:
            for pos in to_set:
                board = ReplaceStringPos(board, pos, token)
    return board


def PrintSnapshot(board, move, token):
    if move is not None:
        print(f"{token} moves to {move}")
    PrintBoard(board)
    print((deformatted_board := board.lower().replace('*', '.')) + ' ' + f"{board.count('x') + board.count('X')}/{board.count('o') + board.count('O')}")
    if move is not None:
        print(f"Possible moves for {(other_token := ['x', 'o'][{'x':1, 'o':0}[token]])}: " + str(MarksListing(deformatted_board, other_token)).replace('[', '').replace(']', ''))
    elif len(MarksListing(deformatted_board, 'x')) != 0 and len(MarksListing(deformatted_board, 'o')) != 0:
        #print(f"x:{MarksListing(board, 'x')} y:{MarksListing(board, 'o')}")
        print(f"Possible moves for {token}: " + str(MarksListing(deformatted_board, token)).replace('[', '').replace(']', ''))
    print('')


def main():
    GenGlobals()
    board, token, move = ProcessArgs()
    PrintSnapshot(MarkMoves(board, token)[0], None, token)#before snapshot
    #move = '19'
    if move is None:
        return
    move = move.lower()
    if move[0].isalpha():#special processing needed
        move = str((ord(move[0]) - ord('a')) + (int(move[1]) - 1) * 8)
    move = int(move)

    move_board = Move(board, move, token)
    board_move = MarkMoves(move_board, ['x', 'o'][{'x':1, 'o':0}[token]])[0]
    PrintSnapshot(board_move, move, token)




if __name__ == '__main__':
    main()
