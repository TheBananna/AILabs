import sys;args = sys.argv[1:]
# Nicholas Bonanno, pd. 6

def SetGlobals(board):
    global width, height, char_set, constraints_row, constraints_column, constraint_lut, neighbors_lut, dot_lut, positions_lut  # constraint_dict is a LUT of the three constraint sets every position is in, neighbors is a LUT of every position's neighbors should be 20 long

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
    seed_strings = []
    for i in args[3:]:
        seed_strings.append(i.upper())#all strings will be upper case

    word_list = []
    with (file := open(args[2])):
        word_list = list(word.replace('\n', '').upper() for word in file.readlines())
    word_list = set(word.upper() for word in word_list)
    return width, height, blocking_squares, word_list, seed_strings

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
    global blocking_squares
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
    if blocking_squares % 2 == 1:
        board[(height // 2) * width + (width // 2)] = '#'#has to be the case if blocking_squares is odd
    return ''.join(board), squares


alphabet = set(chr(i) for i in range(ord('A'), ord('Z') + 2)) | set('?')#question mark for unkown letters


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
    if blocks > blocking_squares: return False, set(), board
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


import random
def find_position(board):#choose the next position to fill with a #
    return find_position_new(board)
    spaces = []
    for i in range(len(board)):
        if board[i] == '-':
            spaces.append(i)
    #will do random for now and see if that works. I can play with or remove the constant seed to change the behavior against fixed test cases too
    random.seed(3)#set seed so still consistent
    if spaces:
        return random.choice(spaces)
    return -1


def find_position_new(board):
    spaces = []
    for i in range(len(board)):
        if board[i] == '-':
            spaces.append(i)

    lowest = (0, 10000000000000000000000)
    for pos in spaces:
        temp_board = [*board]
        temp_board[pos] = '#'
        horizontals, verticals = FindWords(temp_board)
        #average = (sum(i[2] for i in horizontals) + sum(i[2] for i in verticals)) / (len(horizontals) + len(verticals))#average word length
        #if average < lowest[1]:
        #    lowest = (pos, average)
        maximum = max(x[2] for x in list(horizontals) + list(verticals))
        if maximum < lowest[1]:
            lowest = (pos, maximum)
    return lowest[0]




def XWords1(board, invalids):#board and invalid positions
    global width, height, blocking_squares
    if board.count('#') > blocking_squares:
        return []#bad path
    if invalids is None:#for first method call or a branch, change how this works later for greater efficiency by changing invalids to be something that stores recently changed pieces that might have invalids in vicinity
        invalids = list(GetInvalidPositions(board))
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
        invalids = list(set(invalids) | nearby_invalids)#potentially change to set in order to remove these casts, randomizes output order, would also be an optimization
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
    position = find_position(board)
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



################################################################       XWords2 Code        ################################################################



def get_words_horiz(board):#returns word descriptors (start, end, length) for all horizontal words
    horizontals = []
    on_word = False
    current_word_start = 0
    for i in range(len(board)):
        if i % width == 0:#to stop row overruning
            if on_word:
                horizontals.append((current_word_start, i - 1, i - current_word_start))
            current_word_start = i
            on_word = board[i] == '-' or board[i] in alphabet
        if board[i] == '-' or board[i] in alphabet:#if in alphabet the current word position doesn't need to be moved
            if not on_word:
                on_word = True
                current_word_start += 1#add one as it was on a #
        else:
            if on_word:
                on_word = False
                horizontals.append((current_word_start, i - 1, i - current_word_start))
            current_word_start = i
    if on_word:
        horizontals.append((current_word_start, len(board) - 1, len(board) - current_word_start))
    return horizontals


def get_words_vert(board):#returns word descriptors (start, end, length) for all horizontal words
    global width, height
    verticals = []
    current_word_start = 0
    on_word = False
    for x in range(width):
        current_word_start = x
        on_word = board[x] == '-' or board[x] in alphabet
        for n, letter in enumerate(GetColumn(board, x)):
            pos = n * width + x
            if board[pos] == '-' or board[pos] in alphabet:
                if not on_word:
                    on_word = True
                    current_word_start = pos
            else:
                if on_word:
                    on_word = False
                    verticals.append((current_word_start, pos - 1, ((pos - 1) - current_word_start) // width + 1))#plus one to account for total length instead of just distance between
                current_word_start += 1
        if on_word:
            verticals.append((current_word_start, len(board) - ((width - 1) - x) - 1, ((len(board) - ((width - 1) - x)) - current_word_start) // width + 1))
    return verticals




def FindWords(board):#returns a list of horizontal and a list of vertical word descriptors [(start, end)...], [(start, end)...]
    global width, height
    horizontals = tuple(get_words_horiz(board))
    verticals = get_words_vert(board)
    return horizontals, verticals


def PlaceWord(board, pos, word):
    for i in range(len(word)):
        board[pos + i] = word[i]


def PlaceWordVertically(board, pos, word):
    for i in range(len(word)):
        board[pos + i * width] = word[i]


def WordFits(board, pos, word):
    for i in range(len(word)):
        if board[pos + i] == '-':
            continue
        if board[pos + i] != word[i]:
            return False
    return True


letter_index_dict = dict()#{(letter, letter index in word) : [words that satisfy this]...}
letter_index_length_dict = dict()#{(letter, letter index in word, length of word) : [words that satisfy this]...}
length_dict = dict()
#IS NOT FILLED CURRENTLY
letter_word_index_dict = dict()#{letter : [(word, index of letter, index of that letter 2, continue as nessecary)...]...}
length_letters_letter_dict = dict() # {(length, letters)) : {letters occuring after this string for words of length length}}
length_letters_count_dict = dict() # {(length, letters) : count of words that satisfy this criterion}
def AssembleDS(wordlist, board, horizontals, verticals, longest_possible_word):#asemble the DS(s) that will be used to fill the board
    for word in wordlist:
        for n, letter in enumerate(word):
            if (u:=(letter, n)) not in letter_index_dict:#not going to pre setup these so I don't have to trim down the3 dictionary later
                letter_index_dict[u] = set()
            if (q:=(letter, n, len(word))) not in letter_index_length_dict:
                letter_index_length_dict[q] = set()
            if (k:=(len(word))) not in length_dict:
                length_dict[k] = set()
            for i in range(len(word)):
                string = word[0 : i]
                if ((z:=(len(word), string)) not in length_letters_letter_dict):
                    length_letters_letter_dict[z] = set()
                if z not in length_letters_count_dict:
                    length_letters_count_dict[z] = 0
                length_letters_letter_dict[z].add(word[i])
                length_letters_count_dict[z] += 1
            letter_index_dict[u].add(word)
            letter_index_length_dict[q].add(word)
            length_dict[k].add(word)


def GetWordBoardPostiionAssociations(board, horizontals, verticals):#returns a list with the indices for that index's horizontal and vertical word along with how far through it it is
    positions = [[] for i in range(len(board))]# [[horizontals index, verticals index]...for each board position]
    for n, word in enumerate(horizontals):
        for i in range(word[0], word[1] + 1):
            positions[i].append(n)
    for n, word in enumerate(verticals):
        for i in range(word[2]):
            positions[i * width + word[0]].append(n)
    return positions


def GetWord(letter, index, length, placed_words):#will get a word that fulfil this that aren't in placed_words
    for word in letter_index_length_dict[(letter, index, length)]:
        if word not in placed_words:
            placed_words.add(word)
            return word
    return None#failed to find a word that fulfils the requirements that hasn't already been placed


def GetWordFromDescriptor(board, descriptor):
    if descriptor[1] - descriptor[0] + 1 == descriptor[2]:# check if horizontal word
        return ''.join(board[descriptor[0] : descriptor[1] + 1])
    return ''.join([board[i] for i in range(descriptor[0], min(len(board), descriptor[1] + 1), width)])


whole_board_possible_letter_cache = dict()#is only used for length_dict set casting caching
#possible_letter_cache = dict()
def GetPossibleLetters(board, wordD, index):# returns the set of possible letters that can go in this word descriptor at this index
    global horizontals, verticals, word_list

    if (word:=GetWordFromDescriptor(board, wordD)).count('-') == wordD[2]:#if the entire word list is possible here, optimization, remove this somehow as it's a lot of list reads
        if wordD[2] in whole_board_possible_letter_cache: return whole_board_possible_letter_cache[wordD[2]]
        whole_board_possible_letter_cache[wordD[2]] = {word[index] for word in length_dict[wordD[2]]}
        return whole_board_possible_letter_cache[wordD[2]]

    if (u:=(wordD[2], word[0:index])) not in length_letters_letter_dict:
        return set()
    possible_letters = length_letters_letter_dict[wordD[2], word[0:index]]#get the possible letters that coild go in this spot
    #possible_letter_cache[search] = possible_letters
    #print(possible_letters)
    return possible_letters


def NextLetter(board, pos):
    for i in range(pos, len(board)):
        if board[i] == '-':
            return i
    return -1#no empty spaces left


##################################################################
# algorithm
# def PlaceWordsRecursive(board, placed words, pos):
# 	 if the board is complete return it
#
# 	 find what vertical and horizontal word this pos is in
# 	 get possible letters that could go here for the horizontal words
# 	 get possible letters that could go here for the vertical words
#    reverse sort the shared letters by the number of words that include the letters up until this point and the intersecting letter
#	 for each intersecting letter in the sorted list:
#		 board copy = copy of the board
#		 placed words copy = copy of placed words
#		 place the intersecting letter at pos in board copy
#		 if this completes a word and it's not in placed words add it to placed words copy, if it is skip this
#		 if ret_board := PlaceWordsRecursive(board copy, placed words copy, pos of next empty letter position):
#			 return ret_board
#	 return []
##################################################################
best = -1
def PlaceWordsRecursively(board, placed_words, pos):
    global horizontals, verticals, word_list, positions_lut, best, DEBUG

    if pos == -1:#no empty spaces left/base case
        return board
    horiz = horizontals[positions_lut[pos][0]]
    vert = verticals[positions_lut[pos][1]]
    horizontal_word = GetWordFromDescriptor(board, horiz)[0 : pos - horiz[0]]
    vertical_word = GetWordFromDescriptor(board, vert)[0 : (pos - vert[0]) // width]
    if not (horizontal_letters := GetPossibleLetters(board, horiz, pos - horiz[0])): return []#possible letters at this index for possible horizontal words
    if not (vertical_letters := GetPossibleLetters(board, vert, (pos - vert[0]) // width)): return []#if either sets are empty this isn't right as there can be no intersection
    intersections = list(horizontal_letters.intersection(vertical_letters))
    intersections.sort(key=lambda x: min(length_letters_count_dict[(horiz[2], horizontal_word)], length_letters_count_dict[(vert[2], vertical_word)]), reverse=True)
    for intersection in horizontal_letters.intersection(vertical_letters):
        board_copy = [*board]
        placed_words_copy = set(placed_words)
        if len(intersection) != 1:
            breakpoint()
        board_copy[pos] = intersection
        #if DEBUG and (u:=board_copy.count('-')) < best:
        #    PrintBoard(board_copy, width, height)
        #    print('')
        #    best = u
        #if '-' not in (word:=GetWordFromDescriptor(board_copy, horiz)):#finished word
        if (word := GetWordFromDescriptor(board_copy, horiz)) in length_dict[horiz[2]]:
            if word in placed_words: continue#already used word
            placed_words_copy.add(word)
        if (word := GetWordFromDescriptor(board_copy, vert)) in length_dict[vert[2]]:
            if word in placed_words: continue
            placed_words_copy.add(word)
        if ret_board := PlaceWordsRecursively(board_copy, placed_words_copy, NextLetter(board_copy, pos + 1)):
            return ret_board

    return []# not viable path


def PlaceWords(board, word_list):#place words in the board and yields better results until completion
    global best
    best = width * height
    original_board = [*board]#make immutable copy of original board
    global letter_index_dict, letter_word_index_dict, letter_index_length_dict, horizontals, verticals, positions_lut
    horizontals, verticals = FindWords(board)
    positions_lut = GetWordBoardPostiionAssociations(board, horizontals, verticals)
    longest_possible_word = max(max(word[2] for word in horizontals), max(word[2] for word in verticals))
    word_list = list(word for word in word_list if 3 <= len(word) <= longest_possible_word)#cut out not possible words
    AssembleDS(word_list, board, horizontals, verticals, longest_possible_word)
    placed_words = set()
    #breakpoint()
    for word in horizontals:
        length = word[1] - word[0] + 1
        for possible_word in word_list:
            if len(possible_word) == length and WordFits(board, word[0], possible_word):
                if possible_word not in placed_words:
                    placed_words.add(possible_word)
                    PlaceWord(board, word[0], possible_word)
                    break
    yield board#yield the horizontal board

    if board := PlaceWordsRecursively(original_board, set(), NextLetter(original_board, 0)):#vertically filled in board
        yield board
    else:
        print('failure to find better option')



def main():
    global args, width, height, backwards, blocking_squares, seed_string_positions, word_list, DEBUG#blocking_squares will be used as the number of squares left to place
    backwards = []
    DEBUG = False
    if not args:
        DEBUG = True
        args = '5x5 0 "dct20k.txt" "V4x1A"'.replace('"', '').replace('dctEckel.txt', 'dct20k.txt').split(' ')
        args = '9x13 19 "dctEckel.txt" "v2x3#" "v1x8#" "h3x1#" "v4x5##"'.replace('"', '').replace('dctEckel.txt', 'dct20k.txt').split(' ')
        args = '7x7 11 "dctEckel.txt"'.replace('"', '').replace('dctEckel.txt', 'dct20k.txt').split(' ')
        #args = '15x15 37 "dctEckel.txt" "H0x4#" "v4x0#" "h12x3a"'.replace('"', '').replace('dctEckel.txt', 'dct20k.txt').split(' ')
    width, height, blocking_squares, word_list, seed_strings = ProcessArgs(args)
    board, seed_string_positions = PlaceSeedStrings(width, height, seed_strings)
    seed_string_positions = set(seed_string_positions)
    SetGlobals(board)
    if blocking_squares == len(board):
        board = '#' * len(board)
        print(board)
        PrintBoard(board, width, height)
        return
    if DEBUG:
        PrintBoard(board, width, height)
    board, blocks = AddSymmetry([*board])#add initial symmetry to make my life easier
    board = XWords1([*board], None)
    board = list(''.join(board).replace('?', '-'))
    if DEBUG:
        print('')
        PrintBoard(board, width, height)
        print('\nDEBUG END\n')
    for best_board_currently in PlaceWords(board, word_list):
        print(''.join(best_board_currently))
        PrintBoard(best_board_currently, width, height)
        print('')
    #SetGlobals(board)
    #detect invalid positions after the board has been laid out so they can be filled
    #proceed to start filling valid positions and filling invalid ones as made. This order must be tracked in case a recursive algorithm is necessary. Invalid placements would be detected by comparing the current list of invalid positions and comparing against the seed character position set
    #recursive algorithm would ideally be similar to my sudoku one where it goes as far as it can before having to backtrack. Unknown if this is possible
    #detect different square regions and fill them smallest to largest


if __name__ == '__main__':
    main()