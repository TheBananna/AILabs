import sys;args = sys.argv[1:]
# Nicholas Bonanno, pd. 6

def SetGlobals(board):
    global width, height, char_set, constraints_row, constraints_column, constraint_lut, neighbors_lut, dot_lut  # constraint_dict is a LUT of the three constraint sets every position is in, neighbors is a LUT of every position's neighbors should be 20 long

    constraints_column = []
    constraints_row = []
    constraints_diagonal = []
    constraint_lut = [[] for i in range(width * height)]  # each arr is formatted as [row_ind, column_ind, diag1_ind, diag2_ind]

    for i in range(height):
        constraints_row.append(z := list(i * width + j for j in range(width)))
        for j in z:
            constraint_lut[j].append(len(constraints_row) - 1)

    for i in range(width):
        constraints_column.append(z := list(j * width + i for j in range(height)))
        for j in z:
            constraint_lut[j].append(len(constraints_column) - 1)



#rotates a board 90 degrees
def rotate90(board, width, height):
  columns = [''.join(reversed(board[i:len(board):width])) for i in range(width)]
  return ''.join(columns)



def rotate180(board):
    global width, height
    return rotate90(rotate90(board, width, height), width, height)


def ReplaceStringPos(string, pos, new_string):
    return f'{string[0:pos]}{new_string}{string[pos + len(new_string):]}'


def PrintBoard(board, width, height):
    for i in range(height):
        string = ''
        for j in board[i * width:(i + 1) * width]:
            string += f'{j}'
        print(string.strip())


def GetColumn(board, pos):#gets a column from a flattened 2d array string
    lut = constraints_column[constraint_lut[pos][1]]
    return ''.join(list(board[i] for i in lut))


def SetColumn(board, pos, new_column):#sets a column in a flattened 2d array string
    board = list(board)
    for i in range(height):
        board[width * i + pos] = new_column[i]
    return ''.join(board)


def ProcessArgs(args):
    height, width = map(int, args[0].split('x'))
    blocking_squares = int(args[1])
    dict_name = args[2]
    seed_strings = []
    for i in args[3:]:
        seed_strings.append(i.upper())#all strings will be upper case

    return width, height, blocking_squares, dict_name, seed_strings

import re
def PlaceSeedStrings(width, height, seed_strings):
    board = '-' * width * height
    positions = set()#set of all positions seed characters were placed in
    for seed_string in seed_strings:
        y_pos = int(seed_string[1:seed_string.index('X')])
        x_pos = int(seed_string[seed_string.index('X') + 1:re.search(r"\D\d*X\d*", seed_string).end()])
        if seed_string[len(seed_string) - 1].isdigit():#blocking square here
            board = ReplaceStringPos(board, y_pos * width + x_pos, '#')
            continue
        chars = seed_string[re.search(r"\D\d*X\d*", seed_string).end():]#if the seed string passes muster and actually has chars in it to be written it's time to extract those
        if seed_string[0] == 'H':#horizontal placement
            board = ReplaceStringPos(board, y_pos * width + x_pos, chars)
            for i in range(len(chars)):
                positions.add(y_pos * width + x_pos + i)
        else:#will be assumed vertical placement
            for i in range(len(chars)):
                board = ReplaceStringPos(board, width * (y_pos + i) + x_pos, chars[i])
                positions.add(width * (y_pos + i) + x_pos)
    return board, positions


letters = {chr(i) for i in range(ord('A'), ord('Z') + 1)}
def AddSymmetry(board):#adds diagonal symmetry to a board and returns board, the number of blocking squares used by merging the board with it's rotated version or returns None if this would replace a letter with a blocking square
    flipped_board = rotate180(board)
    board = [*board]
    squares = 0
    for i in range(len(board)):
        if board[i] in letters and flipped_board[i] == '#':
            return None#invalid board as no diagonal symmetry could be found
        if board[i] in ['-', '#'] and flipped_board[i] == '#':#array as probably faster than a set at this size
            board[i] = '#'
            squares += 1
    return ''.join(board), squares


directions = [[0,1],[0,-1],[1,0],[-1,0]]
def RecursiveZoneCheck(board, cur_width, cur_height, checked, zone):#checks for blocked off zones
    if (pos := cur_height * width + cur_width) in checked or board[pos] == '#':
        return
    checked.add(pos)
    zone.add(pos)
    for dir in directions:
        if 0 > (cur_width + dir[0]) or (cur_width + dir[0]) >= width or 0 > (cur_height + dir[1]) or (cur_height + dir[1]) >= height or board[pos] == '#':
            continue
        RecursiveZoneCheck(board, cur_width + dir[0], cur_height + dir[1], checked, zone)


valid_board_cache = dict()
def ValidBoard(board):#decides if a board is valid based on whole board effects, should be used after making the board symmetric
    if board in valid_board_cache:
        return valid_board_cache[board]
    checked = set()
    zones = set()
    for y in range(height):#check for all seperated regions to verify there's only one
        for x in range(width):
            zone = set()
            RecursiveZoneCheck(board, x, y, checked, zone)
            zone = frozenset(zone)
            zones.add(zone)
    if frozenset() in zones:
        zones.remove(frozenset())
    if len(zones) > 1:
        valid_board_cache[board] = False, zones
        return False, zones
    valid_board_cache[board] = True, zones
    return True, zones


match3 = re.compile(r'[^#]{3}')#optimization, don't use regex
#optimization, pregenerate the search zones for both columns and  rows for every position
def ValidPosition(board, pos):#checks to see if a position is valid, does not check for board invalid states like there being multiple disconnected zones.
    if board[pos] == '#':
        return True#always a valid position
    column = GetColumn(board, pos % width)
    horizontal = pos % width
    vert = pos // width
    column = column[max(0, vert - 2):vert + 3]#+3 to be inclusive
    column_start = max(0, vert - 2) * width + horizontal#actual board position this column starts at
    column_end = min(width - 1, vert + 2) * width + horizontal  # actual board position this column ends at
    ind = 0
    while reg := match3.search(column, ind):
        ind += 1
        double3 = False  # a 3x3 square could be found
        match = 0
        for i in range(reg.start(), reg.end()):  # go across the regex match to do this check again sideways for each possible vertical position
            row = board[max((max(0, vert - 2) + i) * width, column_start + i*width - 2):min((max(0, vert - 2) + i + 1) * width, column_start + i*width + 3)]#gives the search space for the regex expression
            #row = board[max((max(0, vert - 2) + i) * width, column_start + i*width - 2):min((min(width - 1, vert + 2 + i)) * width, column_start + i*width + 3)]
            #row = board[max(max(0, vert - 2 + i) * width, column_start + i*width - 2):min(min(width, vert + 2 + i) * width, column_start + i*width + 3)]
            if not match3.search(row):  # check within 2 on the row
                break  # all three rows in question must have a regex match
            match += 1
        if match == 3:
            return True
    return False


invalids_cache = dict()
def GetInvalidPositions(board):
    if board in invalids_cache:
        return invalids_cache[board]
    ret = set(n for n, pos in enumerate(board) if not ValidPosition(board, n))#will use this and position of seed characters to know if an invalid placement has been made as then a seed character would be an invalid position
    multiple_zones, zones = ValidBoard(board)
    invalids_cache[board] = ret
    return ret

def SolveMax(board):  # Solve puzzle as far as can go trivially heuristically, return None if
    global blocking_squares#DOESN'T WORK
    invalids = GetInvalidPositions(board)
    for pos in invalids:
        if board[pos] in letters:
            pass
    valid, zones = ValidBoard(board)
    if not valid:
        zones = list(zones)
        zones.sort(key=lambda l: len(l))
        for zone in zones:
            if blocking_squares >= len(zone):
                for i in zone:
                    board[i] = '#'
                blocking_squares -= len(zone)
    while blocking_squares and invalids:
        pos = invalids.pop()
        board[pos] = '#'


def IsSolved(board, square_count):  # must be called after IsInvalid as I don't want to have to call that method twice for performance reasons
    return board.count('#') == square_count


def FillZones(board):
    global blocking_squares
    blocks = board.count('#')
    if blocks > blocking_squares:return False, board
    multiple_zones, zones = ValidBoard(board)
    if multiple_zones:
        zones = list(zones)
        zones.sort(key=lambda x: len(x), reverse=True)
        while blocks < blocking_squares and len(zones) > 0:
            zone = zones.pop()
            blocks += len(zone)
            for pos in zone:
                board[pos] = '#'
        if len(zones) != 0:
            return False, board
    return True, board


def HeuristicSolve(board, allowed):  # is not pure heuristic, when it runs out of puzzles with only one possibility in one of the positions it DFS's the options on the first smallest possibility position
    #board = [*board]  # copies the puzzle array
    if IsSolved((temp := SolveMax(board))[1]):  # checks if the furthest solution from SolveMax is solved and returns if so
        return ''.join(board)
    board = temp

    for position in allowed:
        if not position:  # if any possibility set in allowed is empty then the DFS made a wrong turn somewhere and the code should back out
            return '.'  # signify this with a single dot as to ensure IsSolved doesn't trip on "" somehow

    for temp in Neighbors(board):
        hs = HeuristicSolve(temp[0], temp[1])
        if hs != '.':  # if hs isn't a . then it's a solution and should be propagated upwards
            backwards.append(board)  # to track how the puzzle was solved, not great since multiple characters are inserted for every SolveMax call
            return hs


def Neighbors(board):#generates DFS neighbors to a board that has been solved as far heuristically as I can
    if IsSolved(board, blocking_squares):
        return board
    pos = -1
    invalids = set(GetInvalidPositions(board))
    rets = []
    for n, char in enumerate(board):
        if char == '-' and n in invalids:#if the invalid isn't a - then the board is broke and this isn't a possible path anyways
            temp_board = [*board]
            temp_board[n] = '#'
            sym_pos = (n%width) * width + n//width#get rotated symmetry coordinates
            if temp_board[sym_pos] != '-':#doesn't work
                continue
            temp_board[sym_pos] = '#'
            success,board = FillZones(board)
            if not success:#could not fill in all but 1 of the seperated regions
                return ''
            rets.append((temp_board, n))
    return rets  # sort this by minimum possible word lengths later like in Sudoku


def BruteForce(board, ind):
    global blocking_squares

    # returns a solved pzl or the empty string on failure
    if board.count('#') > blocking_squares:
        return ''#gone to far
    if not ValidBoard(board)[0]:#board is not valid
        return ''
    if ind is not None:#handles first call
        if not ValidPosition(board, ind): return ''#last placed position is not valid
    if IsSolved(board, blocking_squares): return board

    for (neighbor, ind) in Neighbors(board):
        bF = BruteForce(neighbor, ind)
        if bF.puzzle != '': return bF
    return ''


def main():
    global width, height, backwards, blocking_squares#blocking_squares will be used as the number of squares left to place
    backwards = []
    args = '5x5 16 dct20k.txt'.split(' ')
    width, height, blocking_squares, dict_name, seed_strings = ProcessArgs(args)
    board, positions = PlaceSeedStrings(width, height, seed_strings)
    board, blocks = AddSymmetry(board)
    SetGlobals(board)
    blocking_squares -= blocks
    if blocking_squares == len(board):
        board = '#' * len(board)
    print(BruteForce(board, None))
    print('done')
    #SetGlobals(board)
    #detect invalid positions after the board has been laid out so they can be filled
    #proceed to start filling valid positions and filling invalid ones as made. This order must be tracked in case a recursive algorithm is necessary. Invalid placements would be detected by comparing the current list of invalid positions and comparing against the seed character position set
    #recursive algorithm would ideally be similar to my sudoku one where it goes as far as it can before having to backtrack. Unknown if this is possible
    #detect different square regions and fill them smallest to largest



    #print(board)
    #PrintBoard(board, width, height)


if __name__ == '__main__':
    main()