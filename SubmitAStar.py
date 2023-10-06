import sys; args = sys.argv[1:]
#Nicholas Bonanno, pd. 6


def GetDimensions(slider):
    smallest = (0, 8)
    for i in range(2, len(slider) // 2 + 1):
        if len(slider) % i == 0 and abs((d := len(slider) / i) - i) < abs(smallest[0] - smallest[1]):
            smallest = (int(i), int(d))
    return list(reversed(sorted(smallest)))#width x height format


def valid_coords(pos, i, j):
    new_coords = (pos[0] + i, pos[1] + j)
    if 0 <= new_coords[0] < width and 0 <= new_coords[1] < height:
        return new_coords
    return None


neighbor_lut = []
def GenerateNeighborLUT():
    global neighbor_lut
    temp = []
    neighbor_lut = []
    for i in range(width):
        for j in range(height):
            coords = (i, j)
            temp.append([k for k in [valid_coords(coords, 0, 1), valid_coords(coords, 0, -1), valid_coords(coords, 1, 0), valid_coords(coords, -1, 0)] if k is not None])

    for i in temp:
        neighbor_lut.append([j[0] * width + j[1] for j in i])
    #breakpoint()


manhattan_lut = dict()
def GenerateManhatanLUT(slider, target):
    target_dict = {i: (n % width, n // width) for n, i in enumerate(target)}
    global manhattan_lut
    manhattan_lut = dict()
    for i in slider.current:
        manhattan_lut[i] = []
        for j in range(len(slider.current)):
            if i != '_':
                manhattan_lut[i].append(abs(j % width - (u := target_dict[i])[0]) + abs(j // width - u[1]))
            else:
                manhattan_lut[i].append(0)#0 so I don't need an if statement for every character in the slider checking for _


def permutations(string, r):
    if r == 1:
        return string
    l = []
    for c in string:
        l.extend([c + chr for chr in permutations(string.replace(c, ''), r - 1)])
    return l


#ends up being slower than using GetManhattenSum
#potential changes could include increasing the block size
manhattan_block_lut = dict()
def GenerateManhattanBlockLUT(target):#block size is the width and the length of the lists will be the height
    global manhattan_block_lut
    manhattan_block_lut = dict()
    #LUT will have the size of (width * height)! / (width * height - width)! with a depth of height

    for s in permutations(target, width):
        manhattan_block_lut[s] = [GetManhattenSum(Slider(i * width * '_' + s + (height - i - 1) * width * '_', None, None)) for i in range(height)]


class Slider(object):
    __slots__ = ['current', 'previous', 'index']
    def __init__(self, slider, prev, indx):
        self.current = slider
        self.previous = prev
        self.index = indx

    def __lt__(self, other):
        return self.current[0] < self.current[0]

    def GetRows(self):
        string = []
        pos = 0
        for i in range(len(self.current) // height):
            string.append(self.current[pos:pos+width])
            pos += width
        return string

    def GetRow(self, row):
        return self.current[(p := height * row):p + width]


def swap_chars(pos1, pos2, string):
    return f'{string[0:pos1]}{string[pos2]}{string[pos1 + 1:pos2]}{string[pos1]}{string[pos2 + 1:]}' if pos1 < pos2 else f'{string[0:pos2]}{string[pos1]}{string[pos2 + 1:pos1]}{string[pos2]}{string[pos1 + 1:]}'


def Neighbors(slider, parent):#returning a list instead of a generator is significantly faster for some reason, probably cache locality
    return [Slider(swap_chars(slider.index, i, slider.current), slider, i) for i in neighbor_lut[slider.index] if i != parent]


def GetPath(slider):
    path = []
    current = slider
    if current.previous == current:
        return [current]
    while current.previous != current.previous.previous:
        path.append(current)
        current = current.previous
    path.append(current)
    path.append(current.previous)
    return list(reversed(path))


def GenericSolvable(slider, target):
    value_dict = dict()
    slider_pos = slider.index % width, slider.index // height
    target_slider_pos = target.find('_') % width, target.find('_') // width
    inversions = 0
    for n,i in enumerate(target):#allows me to assume that target is in order to see if slider can end up as it
        value_dict[i] = n

    for i in range(len(slider.current)):#counts inversions
        start = slider.current[i]
        for j in slider.current[i + 1:]:
            if j != '_' and start != '_' and value_dict[j] < value_dict[start]:
                inversions += 1

    if width % 2 == 1:
        return inversions % 2 == 0
    if width % 2 == 0:
        if (target_slider_pos[1] - (slider_pos[1]) + 1) % 2 == 0 and inversions % 2 == 1:
            return True
        if (target_slider_pos[1] - (slider_pos[1]) + 1) % 2 == 1 and inversions % 2 == 0:
            return True
    return False


def GetManhattenSum(slider):#using a list in the sum makes this substantially faster than a generator as well, likely for the same reasons, cache locality
    return sum([manhattan_lut[i][n] for n, i in enumerate(slider.current)])


#upper bound calculation for the sum of a slider's elements' Manhattan distances, it's higher than the actual theoretical but calculating the conversion coefficient is really slow and it gets smaller as the sliders get larger so I'll probably leave it at .8 since I doubt anything will have to be higher than that in the tests
def MaximumManhatten(dim):#if you wish to see my work on deriving this just email, it's several pages of scratch work, I figured this out by brute-forcing a lot and looking for patterns
    #works by finding the 1 X K max manhattan and in one step and then using that to find the max manhattan for N x K in one step
    #this is based off of the initial formula's being able to to find the max manhattan for 1 x K and the second ones condensing repeated addition used to advance down the Z x K series where Z is any integer smaller than or equal to K
    #dims will be N x K for comment purposes
    N, K = sorted(dim)#N x K and K x N have same max
    zero_first_dif = 0#0th index 1st finite difference compared to 0 x K, the same as the Maximum Manhattan for 1 x K
    if K % 2 == 0:#K is even
        zero_first_dif = K * K - (u := (K / 2)) * (u + 1)# part after - derived from sequence plugged into oeis.org, n(n-1), and some fiddling until it worked
    else:#K is odd
        zero_first_dif = K * K - ((K + 1) / 2)**2

    def f(Z):#the number of times to multiply by K when in sequence location Z x number>=Z to adjust the output of below to adjust for a growing sequence
        x = Z - 1
        return x * (x + 1) / 2 + math.floor((x + 1) ** 2 / 4)#from oeis.org after manually calculating this for about 10 sequence positions without it

    return int(zero_first_dif * N + f(N) * K * .8) + 1#the .8 and +1 comes from experimental testing showing that the actual maximum manhattan distance being at most .8 of this number, baring 2x2 but those are small enough I don't care since I won't be using them


def MaximumAStar(slider, dims):#to be used with the priority queue
    # the minimum number of moves to solve a puzzle is it's initial Manhattan distance since it can only go up or down by two every move, so that plus the MaximumManhattan should be enough
    return MaximumManhatten(dims) + min(205, GetManhattenSum(slider))#takes at most 205 moves to solve a 4x4 according to wikipedia


def DetermineLowestAStar(prio_queue, prev_lowest):
    for n,i in enumerate(prio_queue[prev_lowest:]):#can depend on order since it's a list
        if len(i) != 0:
            return n + prev_lowest
    return 0#no lowest found


def SolveAStarEpsilon(slider, target):#based on epsilon bound relaxation but epsilon is less than 1 in order to work instead of larger. I thought of this version of it as you can see the wikipedia version uses epsilon larger than 1. I didn't get it at first so I just went with what I thought it meant based on the name and here we are. Mine seems to work better in my testing too so that worked out lol
    EPSILON = .9#can be any value smaller than 1 but the smaller it is the faster it is at the cost of potentially longer than ideal paths being produced. .5 would be nice if we could get a few wrong, but because we can't I have to be more conservative
    #testing showed that .8 was about as small as I could get before errors started cropping up and I was still getting more puzzles out of eckel.txt
    #if you object to me doing this that's understandable, I just see no other ways of making my code faster enough to finish more puzzles in time
    if slider.current == target:
        return slider
    GenerateManhatanLUT(slider, target)#lookup table for the manhattan distance of each character at each index
    openSet = [[] for i in range(1, int(MaximumAStar(slider, (width, height)) * (1 / EPSILON) + 1))]#priority queue
    openSet[1] = [(0, slider)]#no longer attempting to simulate bfs in any way, the pop will take off the most recent added
    closedSet = set()
    k = 0
    lowest = 1
    #breakpoint()
    neighbors = Neighbors#makes ~2% faster, changed to global method instead of instance method for a similar performance improvement
    getmanhattansum = GetManhattenSum#same reason as before, this was never an instance method though
    while True:#will break when done
        k += 1
        #changing lowest if needed, at the end in case any elements get added to lowest's bucket when s is processed
        while not openSet[lowest]:#if this element of the openSet is empty look for the next lowest
            lowest += 1

        level, s = openSet[lowest].pop()#the most recently added slider to lowest's bucket in the priority queue

        if s.current in closedSet:#doesn't continue because then the code that changes lowest if needed doesn't execute leading to a pop on an empty list sometimes
            continue
        closedSet.add(s.current)

        for neighbor in neighbors(s, s.previous.index):
            if neighbor.current in closedSet:#this first since if i is in the closedSet it cannot be the target
                continue
            if neighbor.current == target:
                #print(k)
                return neighbor
            estimate_new = int(round((level + EPSILON + getmanhattansum(neighbor)) * (1 / EPSILON)))
            if estimate_new < lowest:
                lowest = estimate_new
            openSet[estimate_new].append((level + EPSILON, neighbor))#adds i and its level to its respective estimate value bucket in the priority queue


def SolveAStar(slider, target):
    if slider.current == target:
        return slider
    GenerateManhatanLUT(slider, target)#lookup table for the manhattan distance of each character at each index
    openSet = [[] for i in range(1, MaximumAStar(slider, (width, height)) + 1)]#priority queue
    openSet[1] = [(0, slider)]#no longer attempting to simulate bfs in any way, the pop will take off the most recent added
    closedSet = set()
    k = 0
    lowest = 1
    #breakpoint()
    neighbors = Neighbors#makes ~2% faster, changed to global method instead of instance method for a similar performance improvement
    getmanhattansum = GetManhattenSum
    while True:#will break when done
        k += 1
        #changing lowest if needed, at the end in case any elements get added to lowest's bucket when s is processed
        while not openSet[lowest]:#if this element of the openSet is empty look for the next lowest
            lowest += 1

        level, s = openSet[lowest].pop()#the most recently added slider to lowest's bucket in the priority queue
        if s.current in closedSet:#doesn't continue because then the code that changes lowest if needed doesn't execute leading to a pop on an empty list sometimes
            continue
        closedSet.add(s.current)

        for neighbor in neighbors(s, s.previous.index):
            if neighbor.current in closedSet:#this first since if i is in the closedSet it cannot be the target
                continue
            if neighbor.current == target:
                #print(k)
                return neighbor
            estimate_new = level + 1 + getmanhattansum(neighbor)
            openSet[estimate_new].append((level + 1, neighbor))#adds i and its level to its respective estimate value bucket in the priority queue


def SolveAStarManhattanAccelerated(slider, target):
    global width, height
    if slider.current == target:
        return slider
    GenerateManhatanLUT(slider, target)#lookup table for the manhattan distance of each character at each index
    #double bucket queue, first layer is f(x) and second is manhattan distance. This is because we are prioritizing minimizing the distance traveled, making prioritizing by the distance to the target within a bucket useful
    #.7 is from experimental testing as speed will be directly affected by the size of the manhattan buckets
    openSet = [[[] for i in range(int(MaximumManhatten((width, height)) * .7))] for i in range(1, MaximumAStar(slider, (width, height)) + 1)]#priority queue
    openSet[1][0] = [(0, slider)]#no longer attempting to simulate bfs in any way, the pop will take off the most recent added
    closedSet = set()
    k = 0
    lowest_f = 1
    lowest_man = 0
    #breakpoint()
    neighbors = Neighbors#makes ~2% faster, changed to global method instead of instance method for a similar performance improvement
    getmanhattansum = GetManhattenSum#same reason as before, this was never an instance method though
    while True:#will break when done
        k += 1
        #changing lowest if needed, at the end in case any elements get added to lowest's bucket when s is processed
        while not openSet[lowest_f][lowest_man]:#if this element of the openSet is empty look for the next lowest
            if lowest_man == len(openSet[lowest_f]) - 1:
                lowest_f += 1
                lowest_man = 0
            else:
                lowest_man += 1

        level, s = openSet[lowest_f][lowest_man].pop()#the most recently added slider to lowest's bucket in the priority queue
        if s.current in closedSet:#doesn't continue because then the code that changes lowest if needed doesn't execute leading to a pop on an empty list sometimes
            continue
        closedSet.add(s.current)

        for neighbor in neighbors(s, s.previous.index):
            if neighbor.current in closedSet:#this first since if i is in the closedSet it cannot be the target
                continue
            if neighbor.current == target:
                #print(k)
                return neighbor
            estimate_new = level + 1 + (u := getmanhattansum(neighbor))
            if estimate_new == lowest_f and u < lowest_man:
                lowest_man = u
            openSet[estimate_new][u].append((level + 1, neighbor))#adds i and its level to its respective estimate value bucket in the priority queue


def FileRun(filename, SolveMethod):
    global width, height
    sliders = open(filename, 'r').read().replace('.', '_').replace('0', '_').splitlines()
    target = sliders[0]
    #sliders = sliders[0:33]
    t0 = time.time()
    for n, i in enumerate(sliders):
        t1 = time.time()

        width, height = GetDimensions(i)
        GenerateNeighborLUT()
        s = Slider(i, None, i.index('_'))
        s.previous = s
        #breakpoint()
        if not GenericSolvable(s, target): # doesn't work for some reason on the slider set gabor uses
            print(f'{s.current} unsolvable in {time.time() - t1} seconds')
            continue

        ns = SolveMethod(s, target)

        if ns.current == s.current:
            print(f'{s.current} is the root in {time.time() - t1} seconds')
        else:
            print(f'{s.current} solved as {GetMovementString(GetPath(ns))} in {time.time() - t1} seconds')
        #print(f'{n}: {i} solved in {len(GetPath(ns)) - 1} steps in {time.time() - t1} seconds')

    print(f'Total process time: {time.time() - t0}')


def GetMovementString(path):
    global width, height
    str_path = ''

    for i in range(len(path) - 1):
        diff = path[i+1].index - path[i].index
        if diff == 1:
            str_path += 'R'
        elif diff == -1:
            str_path += 'L'
        elif diff == width:
            str_path += 'U'
        elif diff == -width:
            str_path += 'D'
        else:
            return 'ERROR'

    return str_path


import time, math, random
def main():
    global args
    global width, height

    if not args:
        args = ['eckel.txt']
        #args = ['153_A46289E7CDFB']

    if '.' not in args[0]:
        args.append(''.join(sorted(args[0].replace('_', ''))) + '_')
        s = Slider(args[0], None, args[0].index('_'))
        s.previous = s
        width, height = 4,4
        GenerateNeighborLUT()
        SolveAStar(s, args[1])
    else:
        FileRun(args[0], SolveAStarManhattanAccelerated)
        exit()

if __name__ == '__main__':
    main()