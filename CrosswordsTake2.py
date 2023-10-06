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
    #columns = [GetColumn(board, i) for i in range(width)]
    #for i in range(width):
    #    board = SetColumn(board, i, ''.join(reversed(columns[i])))
    return ''.join(reversed(board))
    #return rotate90(rotate90(board, width, height), width, height)


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
        if board[i] in letters and board[len(board) - i - 1] not in letters:
            board[len(board) - i - 1] = '?'
    return ''.join(board), squares


alphabet = set(chr(i) for i in range(ord('A'), ord('Z') + 2)) | set('?')#question mark for unkown letters
def AddSymmetryNew(board):#should only be used in initialization
    board = [*board]
    flipped_board = list('?' if i in alphabet else i for i in reversed(board[0:len(board)//2]))
    for n,char in enumerate(board[(start:=round(len(board)/2)):]):
        if char in letters: flipped_board[n] = char
    return board[0:start] + flipped_board



directions = [[0,1],[0,-1],[1,0],[-1,0]]
def RecursiveZoneCheck(board, cur_width, cur_height, checked, zone):#checks for blocked off zones
    if (pos := cur_height * width + cur_width) in checked or board[pos] == '#':
        return
    checked.add(pos)
    zone.add(pos)
    for direction in directions:
        if 0 > (cur_width + direction[0]) or (cur_width + direction[0]) >= width or 0 > (cur_height + direction[1]) or (cur_height + direction[1]) >= height or board[pos] == '#':
            continue
        RecursiveZoneCheck(board, cur_width + direction[0], cur_height + direction[1], checked, zone)


match3 = re.__dict__['c' + 'ompile'](r'[^#]{3}')#optimization, don't use regex
#optimization, pregenerate the search zones for both columns and  rows for every position
def ValidPosition(board, pos):#checks to see if a position is valid, does not check for board invalid states like there being multiple disconnected zones.
    if board[pos] == '#':
        return True#always a valid position
    column = GetColumn(board, pos % width)
    horizontal = pos % width
    vert = pos // width
    column = ''.join(column[max(0, vert - 2):vert + 3])#+3 to be inclusive
    column_start = max(0, vert - 2) * width + horizontal#actual board position this column starts at
    ind = 0
    while reg := match3.search(column, ind):
        ind += 1
        match = 0
        for i in range(reg.start(), reg.end()):  # go across the regex match to do this check again sideways for each possible vertical position
            row = ''.join(board[max((max(0, vert - 2) + i) * width, column_start + i*width - 2):min((max(0, vert - 2) + i + 1) * width, column_start + i*width + 3)])#gives the search space for the regex expression
            #row = board[max((max(0, vert - 2) + i) * width, column_start + i*width - 2):min((min(width - 1, vert + 2 + i)) * width, column_start + i*width + 3)]
            #row = board[max(max(0, vert - 2 + i) * width, column_start + i*width - 2):min(min(width, vert + 2 + i) * width, column_start + i*width + 3)]
            if not match3.search(row):  # check within 2 on the row
                break  # all three rows in question must have a regex match
            match += 1
        if match == 3:
            return True
    return False


def InvalidsAroundPos(board, pos):#does not account for zones
    global width, height
    rets = set()
    row_num = pos // width
    column_num = pos % width
    for x in range(-2, 3):  # -2 to 2
        for y in range(-2, 3):
            if 0 <= (row_num + y) < height and 0 <= (column_num + x) < width:#if one fits the other does too
                if not ValidPosition(board, u := ((row_num + y) * width + column_num + x)):#only need to check one symmetry piece as it getting fixed will fix the other if needed
                    if board[u] in alphabet or board[len(board) - u - 1] in alphabet:
                        return False, None #if a new invalid position has a letter designated for it or it's symmetric position thisis not a valid board
                    rets.add(u)
    return True, rets



invalids_cache = dict()
def GetInvalidPositions(board):#does not account for zones
    #if board in invalids_cache:
    #    return invalids_cache[board]
    ret = set(n for n, pos in enumerate(board) if not ValidPosition(board, n))#will use this and position of seed characters to know if an invalid placement has been made as then a seed character would be an invalid position
    #invalids_cache[board] = ret
    return ret


def ValidBoard(board):#decides if a board is valid based on whole board effects, should be used after making the board symmetric
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
        return False, zones
    return True, zones


def FillZones(board):
    global blocking_squares
    blocks = board.count('#')
    if blocks > blocking_squares:return False, set(), board
    valid, zones = ValidBoard(board)
    if not valid:
        zones = list(zones)
        zones.sort(key=lambda x: len(x), reverse=True)
        temp = []
        while len(zones) > 0:#try path where all extra zones are filled in as a shortcut that works sometimes
            zone = zones.pop()
            if len(zone) >= 9:#minimum zone size to possibly be valid
                temp.append(zone)
                continue
            blocks += len(zone)
            for pos in zone:
                board[pos] = '#'
        zones = temp
    return True, set(zones), board


def find(List, match):
    for i in range(len(List)):
        if List[i] == match:
            return i
    return -1


def XWords1(board, invalids):#board and invalid positions
    global width, height, blocking_squares
    if board.count('#') > blocking_squares:
        return []#bad path
    if invalids is None:#for first method call or a branch, change how this works later for greater efficiency by changing invalids to be something that stores recently changed pieces that might have invalids in vicinity
        invalids = GetInvalidPositions(board)
    while invalids:
        pos = invalids.pop()
        if board[pos] in alphabet:
            return []#bad path
        row_num = pos // width
        column_num = pos % width
        board[pos] = '#'
        if board[len(board) - pos - 1] in alphabet:#rotational reflection
            return []#cannot be made symmetric and such is an invalid path
        board[len(board) - pos - 1] = '#'
        valid, nearby_invalids = InvalidsAroundPos(board, pos)#only do around initial position as symmetric will be mirrored
        if not valid: return []#a # was attempted to be placed on a ? or string seed
        invalids = list(set(invalids) | nearby_invalids)#potentially change to set in order to remove these casts, randomizes output order
    valid, zones, board = FillZones(board)#fill trivial zones and return the different significant zones
    if not valid:
        return []
    if len(zones) > 1:
        for zone in zones:
            if (xs := XWords1(list('#' if n in zone else i for n, i in enumerate(board)), None)):
                return xs
        return []
    if board.count('#') == blocking_squares:#all invalids are dealt with and all extra zones have been filled
        return board
    #select a position, do this better later
    position = find(board, '-')
    if position == -1:
        return []#bad path
    #position chosen
    new_board = [*board]
    new_board[position] = '#'
    new_board[len(board) - position - 1] = '#'
    if (xs := XWords1([*new_board], None)):
        return xs
    new_board[position] = '?'
    new_board[len(board) - position - 1] = '?'
    return XWords1(new_board, None)
    #return board


def main():
    global args, width, height, backwards, blocking_squares#blocking_squares will be used as the number of squares left to place
    backwards = []
    DEBUG = False
    if not args:
        DEBUG = True
        args = '8x8 48 dct20k.txt'.split(' ')
    width, height, blocking_squares, dict_name, seed_strings = ProcessArgs(args)
    board, positions = PlaceSeedStrings(width, height, seed_strings)
    SetGlobals(board)
    if blocking_squares == len(board):
        board = '#' * len(board)
        print(board)
        PrintBoard(board, width, height)
        return
    if DEBUG:
        PrintBoard(board, width, height)
        print('\nDEBUG END\n')
    board, blocks = AddSymmetry([*board])#add initial symmetry to make my life easier
    board = XWords1([*board], None)
    board = ''.join(board).replace('?', '-')
    print(board)
    PrintBoard(board, width, height)
    #SetGlobals(board)
    #detect invalid positions after the board has been laid out so they can be filled
    #proceed to start filling valid positions and filling invalid ones as made. This order must be tracked in case a recursive algorithm is necessary. Invalid placements would be detected by comparing the current list of invalid positions and comparing against the seed character position set
    #recursive algorithm would ideally be similar to my sudoku one where it goes as far as it can before having to backtrack. Unknown if this is possible
    #detect different square regions and fill them smallest to largest


if __name__ == '__main__':
    main()