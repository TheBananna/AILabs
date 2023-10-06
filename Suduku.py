import sys; args = sys.argv[1:]
#Nicholas Bonanno, pd. 6

from math import *
import time

def GetDimensions(slider):
    global N, h, w
    h = int(sqrt(N))
    while N % h != 0:
        h -= 1
    w = N // h

    w, h = list(reversed(sorted([w, h])))


def SetGlobals(pzl):
    global N, w, h, chars, char_set, constraints_row, constraints_column, constraints_subblock, constraint_lut, neighbors_lut, dot_lut#constraint_dict is a LUT of the three constraint sets every position is in, neighbors is a LUT of every position's neighbors should be 20 long

    N = int(sqrt(len(pzl)))
    GetDimensions(pzl)
    constraint_lut = [[] for i in range(N * N)]
    neighbors_lut = [[] for i in range(N * N)]#is turned into list of sets later
    constraints_row = []
    constraints_column = []
    constraints_subblock = []
    dot_lut = {i:[] for i in range(3 * N)}
    if N == 9:
        chars = [i for i in '123456789']
    elif N == 12:
        chars = [i for i in '123456789ABC']
    elif N == 16:
        chars = [i for i in '0123456789ABCDEF']
    else:#a backup
        chars = [i for i in '123456789']
    char_set = set(chars)
    char_set.add('.')

    for i in range(N):
        constraints_row.append(z := list(i * N + j for j in range(N)))
        for j in z:
            constraint_lut[j].append(len(constraints_row) - 1)

    for i in range(N):
        constraints_column.append(z := list(j * N + i for j in range(N)))
        for j in z:
            constraint_lut[j].append(len(constraints_column) - 1)

    for i in range(N // w):
        for j in range(N // h):
            sub_block = []
            for k in range(h):
                sub_block.extend([i * h * N #correct top left corner of sub block
                                  + N * k   #correct row in sub block
                                  + j * w   #correct horizontal sub block
                                  + z       #correct horizontal index in sub block
                                  for z in range(w)])
            constraints_subblock.append(list(sub_block))
            for k in sub_block:
                constraint_lut[k].append(len(constraints_subblock) - 1)

    for i in range(N * N):
        pos = constraint_lut[i]
        neighbors_lut[i].extend(constraints_row[pos[0]])
        neighbors_lut[i].extend(constraints_column[pos[1]])
        neighbors_lut[i].extend(constraints_subblock[pos[2]])
        neighbors_lut[i] = set(neighbors_lut[i])
        neighbors_lut[i].remove(i)

    for i in range(N * N):
        pos = constraint_lut[i]
        dot_lut[sum(1 if pzl[j] == '.' else 0 for j in neighbors_lut[i])].append(i)
    dot_lut.pop(0)
    #breakpoint()


class Puzzle(object):#uses less memory than list tuple accumulation I think
    __slots__ =  ['previous', 'puzzle']
    def __init__(self, previous, puzzle):
        self.previous = previous
        self.puzzle = puzzle


def permutations(string, r):
    if r == 1:
        return string
    l = []
    for c in string:
        l.extend([c + chr for chr in permutations(string.replace(c, ''), r - 1)])
    return l


def IsValid(pzl, ind=None):
    if ind is None:
        return True#for the first puzzle
    else:
        constraint_pos = constraint_lut[ind]
        row = [pzl.puzzle[i] for i in constraints_row[constraint_pos[0]]]
        row_set = set(row)
        column = [pzl.puzzle[i] for i in constraints_column[constraint_pos[1]]]
        column_set = set(column)
        sub_block = [pzl.puzzle[i] for i in constraints_subblock[constraint_pos[2]]]
        sub_block_set = set(sub_block)

        dot_count = row.count('.')
        if len(row_set.intersection(char_set)) != N - dot_count + (1 if dot_count != 0 else 0):
            return False

        dot_count = column.count('.')
        if len(column_set.intersection(char_set)) != N - dot_count + (1 if dot_count != 0 else 0):
            return False

        dot_count = sub_block.count('.')
        if len(sub_block_set.intersection(char_set)) != w * h - dot_count + (1 if dot_count != 0 else 0):
            return False

        return True


def IsSolved(pzl):#must be called after IsInvalid as I don't want to have to call that method twice for performance reasons
    return pzl.puzzle.count('.') == 0 and len(pzl.puzzle) > 0

ind = 1
def Neighbors(pzl):#I use yield due to how recursive this problem is and I don't want to hog memory at each level. I will likely revisit this later
    global dot_lut, ind
    #while not dot_lut[ind]:
    #    dot_lut.pop(ind)
    #    ind += 1
    #    if ind == 3 * N:
    #        return []
    ind = pzl.puzzle.find('.')#dot_lut[ind].pop()
    return [(Puzzle(pzl, pzl.puzzle.replace('.', j, 1)), ind) for j in chars if j not in neighbors_lut[ind]]


def BruteForce(pzl, ind):
    # returns a solved pzl or the empty string on failure
    if not IsValid(pzl, ind): return Puzzle(None, '')
    if IsSolved(pzl): return pzl

    for neighbor, ind in Neighbors(pzl):
        bF = BruteForce(neighbor, ind)
        if bF.puzzle != '': return bF
    return Puzzle(None, '')


def checkSum(pzl):
    return sum([ord(i) for i in pzl.puzzle]) - 48 * N * N


def GetString(pzl):
    rows = [list(pzl.puzzle[i * N:(i+1) * N]) for i in range(N)]
    for i in range(N):
        for j in range(N // w - 1):
            rows[i].insert((j + 1) * w + j, '|')
        rows[i] = ' '.join(rows[i])
    for i in range(N // h - 1):
        rows.insert((i + 1) * h + i, ''.ljust(N * 2 + rows[0].count('|') * 2 - 1, '-'))#the minus 1 is needed for some reason

    return '\n'.join(rows)


def SolveSlotSet(i, allowed, pzl):#solves up to one position in the set, for now at least
    for j in i:  # for every position in the subblock
        diff = allowed[j]
        if not isinstance(diff, set):
            continue
        for k in i:  # for every other position in the subblock
            if k != j and isinstance(allowed[k], set):
                diff = diff - allowed[k]
        if len(diff) == 1:
            pzl[j] = diff.pop()# will only replace 1 character per run through for now
            diff.add(pzl[j])#to not have the empty set check go off
            return True
    return False


def ScanSolve(allowed, pzl):#scans the puzzle for relatively trivial solutions
    for i in constraints_subblock:  # for every subblock
        if SolveSlotSet(i, allowed, pzl):
            return True
    for i in constraints_row:  # for every subblock
        if SolveSlotSet(i, allowed, pzl):
            return True
    for i in constraints_column:  # for every subblock
        if SolveSlotSet(i, allowed, pzl):
            return True
    return False


def SolveSlotPuzzle(allowed, pzl):
    if ScanSolve(allowed, pzl):
        return


def SolveMax(pzl):#Solve puzzle as far as can go trivially heuristically
    prev = None
    while not IsSolved(Puzzle(None, ''.join(pzl))):#cannot handle multiple solutions
        # if pzl[j] != '.'
        not_allowed = [{pzl[j] for j in neighbors_lut[n]} if i == '.' else i for n, i in enumerate(pzl)]  # list of what a position cannot be

        allowed = [char_set - i if isinstance(i, set) else i for i in not_allowed]
        SolveSlotPuzzle(allowed, pzl)
        if prev == pzl:
            return allowed, pzl
        prev = pzl
    return pzl
        #breakpoint()


def NeighborsHeuristic(pzl, allowed):
    loc = pzl.index('.')
    floc = loc
    for n, i in enumerate(allowed[floc:]):
        if isinstance(i, set) and len(i) < len(allowed[loc]):
            loc = n + floc
    return [pzl[:loc] + [j] + pzl[loc + 1:] for j in allowed[loc]]


def HeuristicSolve(pzl):
    if '.' in char_set:
        char_set.remove('.')
    pzl = [*pzl]

    if IsSolved(Puzzle(None, (u := SolveMax(pzl))[1])):
        return ''.join(pzl)

    allowed = u[0]
    pzl = u[1]

    empty = False
    for i in allowed:
        if isinstance(i, set) and not i:
            empty = True
            break
    if empty:
        return '.'

    for neighbor in NeighborsHeuristic(pzl, allowed):
        hs = HeuristicSolve(neighbor)
        if hs != '.':
            backwards.append(pzl)
            return hs

    return '.'


def main():
    global args, N, w, h, backwards
    backwards = []
    if not args:
        args = ['...1...97..4..9.8....8...1....3....536.....787....2....5...7....1.5..3..49...8...']
        args = ['puzzles.txt']
    if len(args[0]) < 60:#file input
        puzzles = open(args[0], 'r').read().replace('_', '.').replace('0', '.').splitlines()
        #puzzles = puzzles[0:55]
        stime = time.time()
        for i in range(len(puzzles)):
            start = time.time()
            SetGlobals(puzzles[i])
            #ns = BruteForce(Puzzle(None, puzzles[i]), None)
            ns = Puzzle(None, HeuristicSolve(puzzles[i]))
            print(f'{i+1}: {puzzles[i]}')
            print(''.ljust(2 + len(str(i + 1)), ' ') + f'{ns.puzzle} {checkSum(ns)} {time.time() - start}s')
            #print(str(i) + '\t\t' + str(time.time() - start) + '\t\t' + str(checkSum(ns)))
        print()
        print(time.time() - stime)
    else:#puzzle input
        SetGlobals(args[0])
        ns = Puzzle(None, HeuristicSolve(args[0]))#BruteForce(Puzzle(None, args[0]), None)
        print(ns.puzzle + '\n\n\n')
        #for i in reversed(backwards):
        #    print(GetString(Puzzle(None, ''.join(i))) + '\n')
        print(len(backwards))
        if ns.puzzle == '.':
            ns.puzzle = args[0]
        #print(GetString(Puzzle(None, args[0])) + '\n')
        #print(GetString(ns))






if __name__ == '__main__':
    main()