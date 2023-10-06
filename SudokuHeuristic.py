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
    global N, w, h, char_set, constraints_row, constraints_column, constraints_subblock, constraint_lut, neighbors_lut, dot_lut#constraint_dict is a LUT of the three constraint sets every position is in, neighbors is a LUT of every position's neighbors should be 20 long

    N = int(sqrt(len(pzl)))
    GetDimensions(pzl)
    constraint_lut = [[] for i in range(N * N)]
    neighbors_lut = [[] for i in range(N * N)]#is turned into list of sets later
    constraints_row = []
    constraints_column = []
    constraints_subblock = []
    if N == 9:
        chars = [i for i in '123456789']
    elif N == 12:
        chars = [i for i in '123456789ABC']
    elif N == 16:
        chars = [i for i in '0123456789ABCDEF']
    else:#a backup
        chars = [i for i in '123456789']
    char_set = set(chars)

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
    #breakpoint()


def IsSolved(pzl):#must be called after IsInvalid as I don't want to have to call that method twice for performance reasons
    return pzl.count('.') == 0 and len(pzl) > 0


def checkSum(pzl):
    return sum([ord(i) for i in pzl]) - 48 * N * N


def GetString(pzl):
    rows = [list(pzl[i * N:(i+1) * N]) for i in range(N)]
    for i in range(N):
        for j in range(N // w - 1):
            rows[i].insert((j + 1) * w + j, '|')
        rows[i] = ' '.join(rows[i])
    for i in range(N // h - 1):
        rows.insert((i + 1) * h + i, ''.ljust(N * 2 + rows[0].count('|') * 2 - 1, '-'))#the minus 1 is needed for some reason

    return '\n'.join(rows)


#@profile
def SolveSlotSet(positions, allowed, pzl):#solves up to one position in the set, for now at least
    for pos in positions:  # for every position in the subsection
        diff = allowed[pos]
        if diff.__class__ != set:
            continue
        diff = set(diff)
        for other_pos in positions:  # for every other position in the subsection
            if allowed[other_pos].__class__ == set and other_pos != pos:
                diff -= allowed[other_pos]
        if len(diff) == 1:
            pzl[pos] = (add := diff.pop())# will only replace 1 character per run through for now
            allowed[pos] = add
            #diff.add(pzl[pos])#to not have the empty set check go off
            return True, pos, add
    return False, -1, -1


def ScanSolve(allowed, pzl):#scans the puzzle for relatively trivial solutions
    for positions in constraints_subblock:  # for every subblock
        if (temp := SolveSlotSet(positions, allowed, pzl))[0]:
            return temp
    for positions in constraints_row:  # for every row
        if (temp := SolveSlotSet(positions, allowed, pzl))[0]:
            return temp
    for positions in constraints_column:  # for every column
        if (temp := SolveSlotSet(positions, allowed, pzl))[0]:
            return temp
    return False, -1, -1


def SolveSlotPuzzle(allowed, pzl):#in own method in case I expand the heuristics
    return ScanSolve(allowed, pzl)

#@profile
def SolveMax(pzl, allowed):#Solve puzzle as far as can go trivially heuristically
    #if ''.join(pzl) == '.2.81.74.7....31...9...28.5..9.4..874..2.8..316..3.2..3.27...6...56....8.76.51.9.':
        #breakpoint()
    prev = None
    if allowed is None:
        allowed = [char_set - {pzl[pos] for pos in neighbors_lut[n]} if char == '.' else char for n, char in enumerate(pzl)]
    while True:#cannot handle multiple solutions
        if not (temp := SolveSlotPuzzle(allowed, pzl))[0]:
            return allowed, pzl
        for neighbor in neighbors_lut[temp[1]]:
            if allowed[neighbor].__class__ == set:
                allowed[neighbor] = allowed[neighbor] - {temp[2]}
        if prev == pzl:#when this has solved as far as it can go return pzl and allowed
            return allowed, pzl
        prev = [*pzl]#would like to remove cause I don't like an 81 element copy. Was the issue with prev = pzl instead as I assumed it copied by value for some reason
        #breakpoint()


def NeighborsHeuristic(pzl, allowed):
    loc = pzl.index('.')
    floc = loc
    for n, chars in enumerate(allowed[floc:]):
        if chars.__class__ == set and len(chars) < len(allowed[loc]):
            loc = n + floc
    new_alloweds = dict()
    for i in allowed[loc]:
        temp = [set(j) if j.__class__ == set else j for j in allowed]
        for neighbor in neighbors_lut[loc]:
            if temp[neighbor].__class__ == set:
                temp[neighbor] -= {i}
        temp[loc] = i
        new_alloweds[i] = temp

    rets = sorted([(sum(map(len, allow)), key, allow) for key, allow in new_alloweds.items()])
    temp = [(pzl[:loc] + [key] + pzl[loc + 1:], allow) for length, key, allow in rets]
    #temp = [(pzl[:loc] + [j] + pzl[loc + 1:], new_alloweds[j]) for j in sorted(allowed[loc])]#without wrapping allowed[loc] in a sorted() this causes the runtime to fluctuate by about 1 second
    return temp


def HeuristicSolve(pzl, allowed):#is not pure heuristic, when it runs out of puzzles with only one possibility in one of the positions it DFS's the options on the first smallest possibility position
    pzl = [*pzl]#copies the puzzle array
    if IsSolved((temp := SolveMax(pzl, allowed))[1]):#checks if the furthest solution from SolveMax is solved and returns if so
        return ''.join(pzl)

    allowed = temp[0]#an array of sets of the allowed characters at each position or the final character
    pzl = temp[1]

    for position in allowed:
        if not position:#if any possibility set in allowed is empty then the DFS made a wrong turn somewhere and the code should back out
            return '.'#signify this with a single dot as to ensure IsSolved doesn't trip on "" somehow
    
    for temp in NeighborsHeuristic(pzl, allowed):
        hs = HeuristicSolve(temp[0], temp[1])
        if hs != '.':#if hs isn't a . then it's a solution and should be propagated upwards
            backwards.append(pzl)#to track how the puzzle was solved, not great since multiple characters are inserted for every SolveMax call
            return hs

    return '.'#no solutions below this point so return up level


def IsValid(pzl):
    for ind in range(N*N):
        constraint_pos = constraint_lut[ind]
        row = [pzl[i] for i in constraints_row[constraint_pos[0]]]
        row_set = set(row)
        column = [pzl[i] for i in constraints_column[constraint_pos[1]]]
        column_set = set(column)
        sub_block = [pzl[i] for i in constraints_subblock[constraint_pos[2]]]
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


def main():
    global args, N, w, h, backwards
    backwards = []
    if not args:
        args = ['...41...2..6....3....2.........67.8.45............3....2......5..7..8...........1']
        args = ['puzzles.txt']
    if len(args[0]) < 60:#file input
        puzzles = open(args[0], 'r').read().replace('_', '.').replace('0', '.').splitlines()
        #puzzles = puzzles[0:55]
        stime = time.time()
        for i in range(len(puzzles)):
            start = time.time()
            SetGlobals(puzzles[i])
            #ns = BruteForce(Puzzle(None, puzzles[i]), None)
            ns = HeuristicSolve(puzzles[i], None)
            max_solved = 0

            #if not IsValid(ns):
            #    return -1
            print(f'{i+1}: {puzzles[i]}')
            print(''.ljust(2 + len(str(i + 1)), ' ') + f'{ns} {checkSum(ns)} {time.time() - start}s')
            #print(str(i) + '\t\t' + str(time.time() - start) + '\t\t' + str(checkSum(ns)))
        print()
        print(time.time() - stime)
    else:#puzzle input
        SetGlobals(args[0])
        ns = HeuristicSolve(args[0], None)#BruteForce(Puzzle(None, args[0]), None)
        print(ns + '\n\n\n')
        for n,i in enumerate(reversed(backwards)):
            print(GetString(''.join(i)) + '\n')
        #print(len(backwards))
        #print(call_count)
        if ns == '.':
            ns = args[0]

        #print(GetString(Puzzle(None, args[0])) + '\n')
        print(GetString(ns))






if __name__ == '__main__':
    main()