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


manhattan_lut = dict()#has a size of width * height and a varying depth between 2 and 4
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


class Slider(object):
    __slots__ = ['current', 'previous', 'index']
    def __init__(self, slider, prev=None, indx=None):
        self.current = slider
        self.previous = self if prev is None else prev
        self.index = indx if indx is not None else slider.index('_')

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


def Neighbors(slider, parent):#returning a list instead of a generator is significantly faster for some reason, probably cache
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


def GetString(slider):
    ROW_COUNT = 7
    path = GetPath(slider)
    rows_count = math.ceil((math.ceil(height * path.__len__() / ROW_COUNT)) / height) * height
    rows = ['' for i in range(rows_count)]
    pos = 0
    row_pos = 0

    while pos < path.__len__():
        for k in path[pos:pos + ROW_COUNT]:
            for n,l in enumerate(k.GetRows()):
                rows[row_pos + n] = f'{rows[row_pos + n]} {l}'
        pos += ROW_COUNT
        row_pos += height
    ret = ''
    for i in range(0, len(rows), height):
        for j in range(height):
            ret = f'{ret}{rows[i + j]}\n'
        ret = f'{ret}\n'
    return ret[:len(ret)-1]


def ContainsElements(prio_queue):
    for i in prio_queue.values():
        if len(i[0]) or len(i[1]):
            return True
    return False


def Solve(slider, target):
    queue = [slider]
    next_queue = []
    seen = set()
    if slider.current == target:
        return slider
    k = 0
    neighbors = Neighbors
    while len(queue) > 0 or len(next_queue) > 0:
        k += 1
        if len(queue) == 0:
            temp = queue
            queue = next_queue
            next_queue = temp
        slider = queue.pop()
        seen.add(slider.current)
        for i in neighbors(slider):
            if i.current not in seen:
                if i.current == target:
                    #print(k)
                    return i
                seen.add(i.current)
                next_queue.append(i)
    return slider



def GenerateRandom3x3():
    l = [i for i in '12345678_']
    random.shuffle(l)
    return ''.join(l)


def GenerateRandom4x4():
    l = [i for i in '123456789abcdef_']
    random.shuffle(l)
    return ''.join(l)


def GenerateRandomNxN(n):
    if n**2 > 95: return None
    l = [chr(i) for i in range(n**2-1)] + ['_']
    sl = ''.join(l)
    random.shuffle(l)
    return ''.join(l), sl


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


def GenerateSolvable4x4():
    l = [i for i in '123456789abcdef_']
    random.shuffle(l)
    s = Slider(''.join(l))
    while not GenericSolvable(s, '123456789abcdef_'):
        random.shuffle(l)
        s = Slider(''.join(l))
    return s.current


def GetManhattenSum(slider):#using a list in the sum makes this substantially faster than a generator as well, likely for the same reasons, cache
    return sum([manhattan_lut[i][n] for n, i in enumerate(slider.current)])


def PopPriorityQueue(prio_queue, lowest):
    if len(prio_queue[lowest][0]) == 0:
        prio_queue[lowest] = (prio_queue[lowest][1], prio_queue[lowest][0])
    return prio_queue[lowest][0].pop()


def DetermineLowest(prio_queue, prev_lowest):
    for n,i in enumerate(prio_queue[prev_lowest:]):#can depend on order since it's a list
        if len(i[0]) + len(i[1]) != 0:
            return n + prev_lowest
    return 0#no lowest found


def SolveManhatten(slider, target):
    if slider.current == target:
        return slider
    target_dict = {i:(n%width, n//width) for n, i in enumerate(target)}
    GenerateManhatanLUT(slider, target_dict)
    queue = [([], [])]#will never have elements inserted here
    for i in range(1, MaximumManhatten((width, height)) + 1):
        queue.append(([], []))
    queue[1] = ([slider], [])
    seen = set()
    lowest = 1
    k = 0
    neighbors = Neighbors
    while t := PopPriorityQueue(queue, lowest):
        k += 1
        slider = t
        seen.add(slider.current)
        for i in neighbors(slider, slider.index):
            if i.current not in seen:
                if i.current == target:
                    #print(f'k: {k}')
                    return i
                seen.add(i.current)
                if (m := GetManhattenSum(i)) < lowest:
                    lowest = m
                queue[m][1].append(i)

        if len(queue[lowest][0]) == 0:
            queue[lowest] = (queue[lowest][1], queue[lowest][0])
            if len(queue[lowest][0]) == 0:
                lowest = DetermineLowest(queue, lowest)
    return slider


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
            estimate_new = level + 1 + getmanhattansum(neighbor)
            openSet[estimate_new].append((level + 1, neighbor))#adds i and its level to its respective estimate value bucket in the priority queue


#args = ['12345678_']
#args = ['8672543_1']#31 length to solution

#width, height = -1,-1




def RunOne(SolveMethod):
    s = Slider(args[0])
    if len(args) == 2:
        if args[0] == args[1]:
            return s, s

    if not GenericSolvable(s, args[1]):  # checks if solvable if given only the starting condition
        return s, None
    target_dict = {i:(n%width, n//width) for n, i in enumerate(args[1])}
    GenerateManhatanLUT(s, target_dict)
    GenerateNeighborLUT()
    ns = SolveMethod(s, args[1])
    return s, ns


def EckelRun(filename, SolveMethod):
    global width, height
    sliders = open(filename, 'r').read().replace('.', '_').replace('0', '_').splitlines()
    t0 = time.time()
    runs = []
    broke = False
    for i in sliders:
        t1 = time.time()

        width, height = GetDimensions(i)
        s = Slider(i)
        target = ''.join(sorted(i.replace('_', ''))) + '_'
        #breakpoint()
        if not GenericSolvable(s, target):
            runs.append((s, None, time.time() - t1))
            continue

        ns = SolveMethod(s, target)

        if time.time() - t0 > 90:
            break

        runs.append((s, ns, time.time() - t1))
    string = ''
    #breakpoint()


    string += f'Total Solved: {len(runs)}\t\t'
    string += f'Total Solvable: {len([i for i in runs if i[1] is not None])}\t\t'
    string += f'Average Time Solvable: {str(sum(u := [i[2] for i in runs if i[1] is not None])/len(u))[0:6]}s\t\t'
    string += f'Total Time: {str(time.time() - t0)[0:6]}s\t\t'
    string += f'Average Path Length: {str(sum(u := [GetPath(i[1]).__len__() for i in runs if i[1] is not None])/len(u))[0:6]}\t\t'
    print(string)


def Bench3x3(SolveMethod):
    global width, height
    width, height = 3,3
    GenerateNeighborLUT()
    t0 = time.time()
    runs = []
    broke = False
    while time.time() - t0 < 90:
        t1 = time.time()
        i = GenerateRandom3x3()

        width, height = GetDimensions(i)
        s = Slider(i)
        target = ''.join(sorted(i.replace('_', ''))) + '_'
        # breakpoint()
        if not GenericSolvable(s, target):
            runs.append((s, None, time.time() - t1))
            continue

        ns = SolveMethod(s, target)

        if time.time() - t0 > 90:
            break

        runs.append((s, ns, time.time() - t1))

    print(f'{len(runs)} random 3x3 puzzles solved in {time.time() - t0}s')
    print(sum(GetPath(i[1]).__len__() for i in runs if i[1] is not None) / len([i for i in runs if i[1] is not None]))


def Bench4x4(SolveMethod):
    global width, height
    width, height = 4,4
    GenerateNeighborLUT()
    t0 = time.time()
    runs = []
    broke = False
    while time.time() - t0 < 90:
        t1 = time.time()
        i = GenerateRandom4x4()

        width, height = GetDimensions(i)
        s = Slider(i)
        target = ''.join(sorted(i.replace('_', ''))) + '_'
        # breakpoint()
        if not GenericSolvable(s, target):
            runs.append((s, None, time.time() - t1))
            continue

        ns = SolveMethod(s, target)

        if time.time() - t0 > 90:
            break

        runs.append((s, ns, time.time() - t1))
    print(f'{len(runs)} random 4x4 puzzles solved in {time.time() - t0}s')
    print(sum(GetPath(i[1]).__len__() for i in runs if i[1] is not None) / len([i for i in runs if i[1] is not None]))


def FileRun(filename, SolveMethod):
    global width, height
    sliders = open(filename, 'r').read().replace('.', '_').replace('0', '_').splitlines()
    target = sliders[0]
    sliders = sliders[0:31]
    t0 = time.time()
    for n, i in enumerate(sliders):
        t1 = time.time()

        width, height = GetDimensions(i)
        GenerateNeighborLUT()
        s = Slider(i)
        #breakpoint()
        if not GenericSolvable(s, target):
            continue

        ns = SolveMethod(s, target)

        print(f'{n}: {i} solved in {len(GetPath(ns)) - 1} steps in {time.time() - t1} seconds')

    print(f'Total process time: {time.time() - t0}')


def TestTwo3x3(Solve1, Solve2):
    global width, height
    width, height = 3,3
    GenerateNeighborLUT()
    t0 = time.time()
    runs = []
    while time.time() - t0 < 30:
        t1 = time.time()
        i = GenerateRandom3x3()

        width, height = GetDimensions(i)
        s = Slider(i)
        target = ''.join(sorted(i.replace('_', ''))) + '_'
        # breakpoint()
        if not GenericSolvable(s, target):
            runs.append((s, None, time.time() - t1))
            continue

        ns1 = Solve1(s, target)
        ns2 = Solve2(s, target)
        if ns1.current != ns2.current:
            print(f'Wrong Output On {s.current} with {ns1.current} and {ns2.current}')
        else:
            print(f'Pass {s.current}')


import time, math, random
def main():
    global args
    global width, height
    args = ['eckel.txt']
    #width, height = 3,3
    #GenerateNeighborLUT()


    #EckelRun('eckel.txt', SolveAStar)
    #EckelRun('eckel.txt', SolveManhatten)
    #Bench3x3(Solve)
    #Bench4x4(Solve)
    #Bench4x4(Solve)
    #Bench3x3(Solve)
    #Bench3x3(SolveAStarEpsilon)
    Bench3x3(SolveAStar)
    #Bench4x4(SolveAStarEpsilon)

    #FileRun('eckel.txt', SolveAStar)
    #eight, width = 4,4
    #args = ['ADHKFCBLNIJGE_MO', 'ABCDEFGHIJKLMNO_']
    #RunOne(SolveAStar)
    #TestTwo3x3(SolveManhatten, SolveAStar)
    exit()
    if len(args) == 1:
        if '.' not in args[0]:
            args.append(''.join(sorted(args[0].replace('_', ''))) + '_')
        else:
            FileRun(args[0], SolveAStar)
            exit()
        width, height = GetDimensions(args[0])

        t0 = time.time()
        s, ns = RunOne(SolveAStar)

        if ns is None:
            print(GetString(s))
            print('Steps: -1')
        else:
            print(GetString(ns))
            print(f'Steps: {GetPath(ns).__len__() - 1}')

        tf = time.time()
        print(f'Time: ' + f'{tf - t0}'[0:4] + 's')
    else:
        width, height = 3,3
        #string = 'Version: 1.1\t'#A slightly optimized version of the one I submitted
        #string = 'Version: 1.1.1\t'#bug fix on valid_coordinates where I swapped the x and y for the swap_chars in the slider index calculation, i[0] * width + i[1] instead of i[1] * width + i[0]
        #string = 'Version 1.1.2\t'#bug fix for not including scientific notation on average impossible time, making it look like it was taking multiple seconds
        #string = 'Version: 2.0\t'#Manhattan speedup is significant enough I think it is worth making this version 2
        string = 'Version: 4.0\t'#Between the A*, Manhattan distance LUT, and epsilon acceleration I say this is worth two more versions
        runs = []

        for i in range(500):
            args = [GenerateRandom3x3(), '12345678_']
            t0 = time.time()
            s, ns = RunOne(SolveAStar)
            tf = time.time()
            runs.append((s, ns, tf - t0))

        string += f'Time: {str(sum([i[2] for i in runs]))[0:4]}s\t\t'
        impossible_time = sum([i[2] for i in runs if i[1] is None])/len([i for i in runs if i[1] is None])
        string += f'Average time impossible: {str(impossible_time)[0:4]}{str(impossible_time)[str(impossible_time).find(chr(101)):]}s\t\t'
        string += f'# impossible: {len([i for i in runs if i[1] is None])}\t\t'
        string += f'Average path length: {str(sum([len(GetPath(i[1])) - 1 for i in runs if i[1] is not None and i[0] != i[1]])/len([i for i in runs if i[1] is not None and i[0] != i[1]]))[0:4]}\t\t'
        string += f'Average time possible: {str(sum([i[2] for i in runs if i[1] is not None])/len([i for i in runs if i[1] is not None]))[0:6]}s\t\t'


        print(string)
        #breakpoint()

if __name__ == '__main__':
    main()