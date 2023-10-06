import sys;args = sys.argv[1:]
# Nicholas Bonanno, pd. 6
LIMIT_AB = 12
MAX_AB = 5
GAMESINTOURNAMENT = 100
import random



def ReplaceStringPos(string, pos, new_string):
    return f'{string[0:pos]}{new_string}{string[pos + 1:]}'

def GenGlobals():
    global constraints_column, constraints_row, constraints_diagonal, constraint_lut, mark_lut, marks_for_char_cache, LIMIT_AB, EDGES, NEXT_TO_EDGES
    marks_for_char_cache = dict()
    constraints_column = []
    constraints_row = []
    constraints_diagonal = []
    constraint_lut = [[] for i in range(64)]  # each arr is formatted as [row_ind, column_ind, diag1_ind, diag2_ind]

    for i in range(8):
        constraints_row.append(z := list(i * 8 + j for j in range(8)))
        for j in z:
            constraint_lut[j].append(len(constraints_row) - 1)

    for i in range(8):
        constraints_column.append(z := list(j * 8 + i for j in range(8)))
        for j in z:
            constraint_lut[j].append(len(constraints_column) - 1)

    # generate both sets of diagonals, slopes of 1 and -1
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

    for n, i in enumerate(constraints_column[0]):
        diagonal = []
        pos = i
        for j in range(8 - n):
            diagonal.append(pos)
            pos += 9
        constraints_diagonal.append(diagonal)
        for j in diagonal:
            constraint_lut[j].append(len(constraints_diagonal) - 1)
    for n, i in enumerate(constraints_row[0][1:]):
        diagonal = []
        pos = i
        for j in range(8 - (n + 1)):
            diagonal.append(pos)
            pos += 9
        constraints_diagonal.append(diagonal)
        for j in diagonal:
            constraint_lut[j].append(len(constraints_diagonal) - 1)

    EDGES = set(constraints_column[0]) | set(constraints_column[7]) | set(constraints_row[0]) | set(constraints_row[7])
    NEXT_TO_EDGES = set(constraints_column[1][1:7]) | set(constraints_column[6][1:7]) | set(constraints_row[1][1:7]) | set(constraints_row[6][1:7])


def PrintBoard(board):
    for i in range(8):
        string = ''
        for j in board[i * 8:(i + 1) * 8]:
            string += f'{j}  '
        print(string.strip())


mark_list_cache = dict()#requires the reversed constraint groups to be separated as this  only works left to right atm
#@profile
def MarkList(pos_list, board, continue_char, ind, mark_pos, pos):#records a set of moves
    #line = tuple(board[i] for i in pos_list[ind])
    #if((u:=(line, continue_char)) in mark_list_cache):
    #    mark_pos.extend(pos_list[ind][i] for i in mark_list_cache[u])
    hit_char = False
    #mark_pos_start_index = len(mark_pos)
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
    reverse = list(reversed(pos_list[ind]))#[regenerate these and add them to the pos_list inline
    for i in reverse[reverse.index(pos) + 1:]:
        if board[i] == continue_char:
            hit_char = True
            continue
        elif board[i] == '.':
            if hit_char:
                mark_pos.append(i)
            break
        else:
            break
    #mark_list_cache[u] = list(pos_list[ind].index(i) for i in mark_pos[mark_pos_start_index:])
    #pass


#records all possible move positions
def MarksForChar(board, pos, char):
    indicies = constraint_lut[pos]
    mark_pos = []
    continue_char = ['x', 'o'][{'x': 1, 'o': 0}[char]]
    MarkList(constraints_row, board, continue_char, indicies[0], mark_pos, pos)  # rows
    MarkList(constraints_column, board, continue_char, indicies[1], mark_pos, pos)  # columns
    MarkList(constraints_diagonal, board, continue_char, indicies[2], mark_pos, pos)  # diagonals 1
    MarkList(constraints_diagonal, board, continue_char, indicies[3], mark_pos, pos)  # diagonals -1

    return mark_pos

marks_listing_cache = dict()
def MarksListing(board, token):  # list of possible moves
    global marks_listing_cache
    if (board, token) in marks_listing_cache:
        return marks_listing_cache[(board, token)]
    marks_pos = []
    for n, i in enumerate(board):
        if i == token:  # check all moves coming off of this
            marks_pos.extend(MarksForChar(board, n, token))
    marks_listing_cache[(board, token)] = list(set(marks_pos))
    return list(set(marks_pos))


def ProcessArgs(args):
    board = '.' * 27 + "ox......xo" + '.' * 27
    token = None
    moves = []
    if len(args) >= 3:
        pos = 0
        if args[pos].__len__() == 64:
            board = args[0].lower()
            pos += 1
        if args[pos].lower() == 'x' or args[pos].lower() == 'o':
            token = args[pos].lower()
            pos += 1
        for i in args[pos:]:
            moves.append(i)
    if len(args) == 2:
        if args[0].__len__() == 64:
            board = args[0].lower()
        elif args[0].lower() == 'x' or args[0].lower() == 'o':
            token = args[0].lower()
        else:
            moves = [args[0].lower()]

        if args[1].__len__() == 64:
            board = args[1].lower()
        elif args[1].lower() == 'x' or args[1].lower() == 'o':
            token = args[1].lower()
        else:
            moves = [args[1].lower()]
    if len(args) == 1:
        if args[0].__len__() == 64:
            board = args[0].lower()
        elif args[0].lower() == 'x' or args[0].lower() == 'o':
            token = args[0].lower()
        else:
            moves = [args[0].lower()]
    moves = [i.lower() for i in moves]
    moves = [int(str((ord(move[0]) - ord('a')) + (int(move[1]) - 1) * 8)) if not move.isdigit() else int(move) for move in moves]
    if token is None:
        token = 'x'
    ret_moves = []
    for move in moves:
        if move >= 0:
            ret_moves.append(move)
    return board, token, ret_moves


def Move(board, move, token):  # plays piece and then updates the board
    board = ReplaceStringPos(board, move, token)#add .upper() after token to make the added token capitalized
    constraint_indx = constraint_lut[move]
    row = constraints_row[constraint_indx[0]]
    row, row2 = row[row.index(move) + 1:], reversed(row[0:row.index(move)])
    column = constraints_column[constraint_indx[1]]
    column, column2 = column[column.index(move) + 1:], reversed(column[0:column.index(move)])
    diag1 = constraints_diagonal[constraint_indx[2]]
    diag1, diag12 = diag1[diag1.index(move) + 1:], reversed(diag1[0:diag1.index(move)])
    diag2 = constraints_diagonal[constraint_indx[3]]
    diag2, diag22 = diag2[diag2.index(move) + 1:], reversed(diag2[0:diag2.index(move)])

    continue_token = ['x', 'o'][{'x': 1, 'o': 0}[token]]
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


def ScoreBoardAbsolute(board, token):#for when the whole game space is viewable
    return board.count(token) - board.count({'x':'o', 'o':'x'}[token])

def PositionSafe(board, other_token, loc):#is this position on the board absolutely safe; e.g. can never be taken under any circumstances in this game
    if loc in CORNERS:#if the position is inherently safe don't evaluate it
        return True
    indx = constraint_lut[loc]
    safes = [False, False, False, False, False, False, False, False]
    #holds off on reversing in case it's not needed. All standard and then reversed because it looked better
    for n, positions in enumerate([constraints_row[indx[0]], constraints_column[indx[1]], constraints_diagonal[indx[2]], constraints_diagonal[indx[3]], reversed(constraints_row[indx[0]]), reversed(constraints_column[indx[1]]), reversed(constraints_diagonal[indx[2]]), reversed(constraints_diagonal[indx[3]])]):
        if n > 3:
            if safes[n - 4]:#already safe in the other direction
                continue
            else:
                return False#potential direction of attack found
        for pos in positions:
            if board[pos] == '.' or board[pos] == other_token:
                break
            if pos == loc:
                safes[n] = True
                break
    if sum(max(safes[i], safes[i + 4]) for i in range(4)) == 4:
        return True
    return False


def GetSafePositions(board, token):#can be tweaked to ignore inherently safe positions
    other_token = ['x', 'o'][{'x': 1, 'o': 0}[token]]
    return {pos for pos in range(64) if PositionSafe(board, other_token, pos)}


board_weights = [#full board weight, ignoring corners as i have a better solution for that
    0,   0,   20, 20, 20, 20, 0,   0,
    0,   0,   -10,-10,-10,-10,0,   0,
    20,  -10, -10, -10, -10, -10, -10, 20,
    20,  -10, -10, 0,  0,  -10, -10, 20,
    20,  -10, -10, 0,  0,  -10, -10, 20,
    20,  -10, -10, -10, -10, -10, -10, 20,
    0,   0,   -10,-10,-10,-10,0,   0,
    0,   0,   20, 20, 20, 20, 0,   0
]
board_cache = dict()
CORNERS = {0, 7, 56, 63}
def ScoreBoardHeuristic(board, token):#attempts to play off of safe positions into safe positions. improvement could be to aggressively seek out safe positions when not having any. agggressive play to get corners would also be good
    if (board, token) in board_cache:
        return board_cache[(board, token)]

    NEXT_TO_CORNERS = {0: [1, 8, 9], 7: [6, 15, 14], 56: [48, 57, 49], 63: [62, 55, 54]}
    SAFE_POSITIONS = CORNERS | EDGES | GetSafePositions(board, token)


    other_token = ['x', 'o'][{'x': 1, 'o': 0}[token]]
    score = 0#arbitrary score, positive good, negative bad
    token_pos = set(n if i == token else -1 for n, i in enumerate(board)) | {-1}
    other_token_pos = set(n if i == other_token else -1 for n, i in enumerate(board)) | {-1}
    token_moves = MarksListing(board, token)
    other_token_moves = MarksListing(board, other_token)
    token_pos.remove(-1)
    other_token_pos.remove(-1)

    score += (len(token_pos.intersection(CORNERS)) - len(other_token_pos.intersection(CORNERS))) * 150#score for corner possession and loss of score for enemy corner position
    score -= (sum([(board[s[1][0]] == token) + (board[s[1][1]] == token) + (board[s[1][2]] == token) for s in NEXT_TO_CORNERS.items() if board[s[0]] != token]) - sum([(board[s[1][0]] == other_token) + (board[s[1][1]] == other_token) + (board[s[1][2]] == other_token) for s in NEXT_TO_CORNERS.items() if board[s[0]] != other_token])) * 50
    #worse to lose a corner than not have it right now
    #score -= (len(token_pos.intersection(NEXT_TO_CORNERS)) - len(other_token_pos.intersection(NEXT_TO_CORNERS))) * 25#don't want to be next to corners but good if the enemy is, less important that owning corners though
    #score += (len(token_pos) - len(other_token_pos)) * 5#the multiplier is arbitrary and will be changed as seen fit
    #score += (len(token_pos.intersection(EDGES)) - len(other_token_pos.intersection(EDGES))) * 10#try to play on edges
    #score -= (len(token_pos.intersection(NEXT_TO_EDGES)) - len(other_token_pos.intersection(EDGES))) * 10#try not to play next to edges
    #score = 1 / (len(other_token_moves) + 1) #attempt to maximize our potential moves and minimize potential enemy moves
    score += (len(token_moves) - len(other_token_moves)) * 20#attempt to minimize enemy moves and maximize my own
    score -= 1000 if len(token_moves) < 2 and len(token_moves) - len(other_token_moves) < 0 else 0#try to not have to pass or get skunked
    score += 1000 if len(other_token_moves) < 2 and len(other_token_moves) - len(token_moves) < 0 else 0#try to skunk the opponent
    score += len(SAFE_POSITIONS) * 50#attempt to get stable areas

    #score += sum({token:1, other_token:-1, '.':0}[board[i]] * board_weights[i] for i in range(64))
    board_cache[(board, token)] = score
    return score


def EvaluateMove(board, token, move):
    new_board = Move(board, move, token)#.lower()
    new_score = ScoreBoardHeuristic(new_board, token)
    return new_score


def HeuristicDecideMove(board, token):
    moves = list((move, EvaluateMove(board, token, move)) for move in MarksListing(board, token))#(move, score)
    highest = (-1, -100000000000000000)#move, score
    for move, score in moves:
        if score > highest[1]:
            highest = (move, score)
    return highest[0]


def GameOver(board):
    move_count = len(MarksListing(board, 'x')) + len(MarksListing(board, 'o'))
    if move_count == 0:
        return True
    else:
        return False


def alphabeta_iterative(board, token, alpha, beta):
    active_token = token
    queue = list(i + [[]] for i in MarksListing(board, token))
    next_queue = []
    best_move = (-10000, [])
    best_enemy_move = (-10000, [])
    for i in range(3):#depth target
        for move in queue:
            new_board = Move(board, move, token)
            score = ScoreBoardHeuristic(new_board, active_token)

            pass#fix issues first


def alphabeta(board, token, alpha, beta, depth=-1):
    if depth == 1:#should return up now
        return [ScoreBoardAbsolute(board, token), [board]]
    moves = MarksListing(board, token)
    best_move = [-10000, []]
    if len(moves) == 0:
        if len(MarksListing(board, {'x':'o', 'o':'x'}[token])):#if a pass needs to happen
            neg = alphabeta(board, {'x':'o', 'o':'x'}[token], -beta, -alpha, depth - 1)
            neg[1].append(-1)
            neg[0] *= -1
            return neg
        return [ScoreBoardAbsolute(board, token), [board]] if depth < 0 else [ScoreBoardHeuristic(board, token), [board]] # when there are no moves
    moves = [(Move(board, move, token), move) for move in moves]

    for move in moves:
        negamax_move = alphabeta(move[0], {'x':'o', 'o':'x'}[token], -beta, -alpha, depth - 1)
        negamax_move = [negamax_move[0] * -1, negamax_move[1]]
        if negamax_move[0] < alpha: continue
        if negamax_move[0] > beta: return [negamax_move[0], []]
        if negamax_move[0] > best_move[0]:
            best_move = negamax_move
            best_move[1].append(move[1])
        alpha = negamax_move[0] + 1
    return best_move


def TerminalNegaMax(board, token):#will return a move
    global LIMIT_AB
    if board.count('.') < LIMIT_AB:
        move_sequence = alphabeta(board, token, -65, 65)[1][1:]
        return move_sequence[len(move_sequence) - 1]
    else:
        #return HeuristicDecideMove(board, token)
        move_sequence = alphabeta(board, token, -1000000000, 1000000000, MAX_AB)[1][1:]
        return move_sequence[len(move_sequence) - 1]


def playGame(token, self=lambda board, moves, token: TerminalNegaMax(board, token), board='.' * 27 + "ox......xo" + '.' * 27, moves=None):
    move_set = set()
    other_token = {'x':'o', 'o':'x'}[token]
    active_token = 'x' if board == '.' * 27 + "ox......xo" + '.' * 27 else token
    played_moves = []
    if moves is not None:#to play a pre-recorded game
        for move in moves:
            if move == -1:
                active_token = {'x':'o', 'o':'x'}[active_token]
                continue
            board = Move(board, move, active_token)
            PrintSnapshot(board, move, active_token)
            played_moves.append((move, active_token, ScoreBoardAbsolute(board, active_token)))
            active_token = {'x': 'o', 'o': 'x'}[active_token]
    if moves is not None:
        print(played_moves)
        return [played_moves, board.count(token), board.count(other_token), token]

    while not GameOver(board):
        moves = MarksListing(board, active_token)
        if len(moves) == 0:
            active_token = {'x':'o', 'o':'x'}[active_token]
            played_moves.append(-1)#a pass
            continue
        if active_token == token:#smart player
            move = self(board, moves, token)
        else:#random player
            move = random.choice(moves)
        board = Move(board, move, active_token)
        played_moves.append(move)
        #PrintSnapshot(board, move, active_token)
        active_token = {'x':'o', 'o':'x'}[active_token]

    return [played_moves, board.count(token), board.count(other_token), token]


def playTournament():
    scores = []
    token = 'x'
    for i in range(GAMESINTOURNAMENT):
        stats = playGame(token)
        token = {'x':'o', 'o':'x'}[token]
        scores.append((max(-64, stats[1] - stats[2]), max(0, stats[1]), min(64, stats[2]), stats))
    print('')
    for i in range(10):
        print(''.join(str(k[0]).rjust(2, '0').rjust(4, ' ') for k in scores[i * 10 : (i + 1) * 10]))
    print(f'My Token Count: {sum(i[1] for i in scores)}')
    print(f'Total Token Count: {sum(i[1] + i[2] for i in scores)}')
    print(f'Score So Far: {str(sum(i[1] / (i[1] + i[2]) for i in scores))[0:4]}%\n')

    for i in sorted(scores)[0:2]:
        game = ''.join(str(i).rjust(2, '_') for i in i[3][0])
        print(f'Game {scores.index(i) + 1} as {i[3][3]} => {i[0]}: {game}')

    print('')
    print(f'N = {LIMIT_AB}')

def PrintSnapshot(board, move, token):
    moves = set(MarksListing(board, token))
    if move is not None:
        print(f"{token} moves to {move}")
        PrintBoard(''.join(i if n not in moves or n == move else '*' for n, i in enumerate(ReplaceStringPos(board, move, token.upper()))))
    else:
        PrintBoard(''.join(i if n not in moves else '*' for n, i in enumerate(board)))
    print((deformatted_board := board.lower().replace('*', '.')) + ' ' + f"{board.count('x') + board.count('X')}/{board.count('o') + board.count('O')}")
    enemy_token = {'x':'o', 'o':'x'}[token]
    other_token = enemy_token if len(MarksListing(board,enemy_token)) else token
    x_moves = len(MarksListing(deformatted_board, 'x'))
    o_moves = len(MarksListing(deformatted_board, 'o'))
    if move is not None and not (x_moves == 0 and o_moves == 0):
        print(f"Possible moves for {other_token}: " + str(MarksListing(deformatted_board, other_token)).replace('[', '').replace(']', ''))
        print('')
        return
    if x_moves != 0 and o_moves != 0:
        print(f"Possible moves for {token}: " + str(MarksListing(deformatted_board, token)).replace('[', '').replace(']', ''))
    elif x_moves != 0:
        print(f"Possible moves for x: " + str(MarksListing(deformatted_board, 'x')).replace('[', '').replace(']', ''))
    elif o_moves != 0:
        print(f"Possible moves for o: " + str(MarksListing(deformatted_board, 'o')).replace('[', '').replace(']', ''))
    print('')


import time
import ctypes
class Strategy:
    logging = True
    def best_strategy(self, board, player, best_move, still_running):
        GenGlobals()
        best_move.value = HeuristicDecideMove(board, player)#for timeout insurance
        print(best_move.value)
        best = TerminalNegaMax(board, player)
        #PrintSnapshot(board, best, player)
        #print('')
        #PrintBoard(board)
        #print(len(str(int(best))))
        #print(isinstance(best, str))
        #print(isinstance(best, int))

        #print(int(best))
        if board[best] != '.':
            raise Exception()
        #print(board[best])
        with best_move.get_lock():
            best_move.value = int(best)
        #print(isinstance(best_move.value, (int)))
        print(best_move.value)
        print('\n\n\n\n\n')