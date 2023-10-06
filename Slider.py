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
    temp = []
    for i in range(width):
        for j in range(height):
            coords = (i, j)
            temp.append([k for k in [valid_coords(coords, 0, 1), valid_coords(coords, 0, -1), valid_coords(coords, 1, 0), valid_coords(coords, -1, 0)] if k is not None])

    for i in temp:
        neighbor_lut.append([j[0] * width + j[1] for j in i])
    #breakpoint()

class Slider:
    def __init__(self, slider, prev=None, indx=None):
        self.current = slider
        self.previous = self if prev is None else prev
        self.index = indx if indx is not None else slider.index('_')

    def GetRows(self):
        string = []
        pos = 0
        for i in range(len(self.current) // height):
            string.append(self.current[pos:pos+width])
            pos += width
        return string

    def swap_chars(self, pos1, pos2, string):
        return f'{string[0:pos1]}{string[pos2]}{string[pos1 + 1:pos2]}{string[pos1]}{string[pos2 + 1:]}' if pos1 < pos2 else f'{string[0:pos2]}{string[pos1]}{string[pos2 + 1:pos1]}{string[pos2]}{string[pos1 + 1:]}'

    #def IfValid(self, self_index, i, j):
    #    if self.valid_coordinates(c := (self.slider_pos[0] + i, self.slider_pos[1] + j)):
    #        s = self.Copy()
    #        s.slider_pos = c
    #        #s.index = c[1] * width + c[0]
    #        s.current = self.swap_chars(self_index, c[1] * width + c[0], self.current)
    #        return s
    #    return None

    def Neighbors(self):
        return [Slider(self.swap_chars(self.index, i, self.current), self, i) for i in neighbor_lut[self.index]]

    def GetRow(self, row):
        return self.current[(p := height * row):p + width]


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



import math
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
    while len(queue) > 0 or len(next_queue) > 0:
        if len(queue) == 0:
            temp = queue
            queue = next_queue
            next_queue = temp
        slider = queue.pop()
        seen.add(slider.current)
        for i in slider.Neighbors():
            if i.current not in seen:
                if i.current == target:
                    return i
                seen.add(i.current)
                next_queue.append(i)
    return slider


import random
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
    val = 0
    inversions = 0
    for i in target:#allows me to assume that target is in order to see if slider can end up as it
        value_dict[i] = val
        val += 1

    for i in range(len(slider.current)):#counts inversions
        start = slider.current[i]
        for j in slider.current[i:]:
            if j != '_' and start != '_' and value_dict[j] < value_dict[start]:
                inversions += 1

    if width % 2 == 1 and inversions % 2 == 0:
        return True
    if width % 2 == 0:
        if (height - (slider_pos[1])) % 2 == 0 and inversions % 2 == 1:
            return True
        if (height - (slider_pos[1])) % 2 == 1 and inversions % 2 == 0:
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


def GetManhattenSum(slider, target_dict):
    return sum(abs(n % width - (u := target_dict[i])[0]) + abs(n // width - u[1]) for n,i in enumerate(slider.current))


def PopPriorityQueue(prio_queue, lowest):
    i = -1
    for n, j in enumerate(prio_queue[lowest:]):
        if len(j[0]) + len(j[1]) != 0:
            i = n + lowest
            break
    if i == -1:
        return False
    if len(prio_queue[i][0]) == 0:
        prio_queue[i] = (prio_queue[i][1], prio_queue[i][0])
    return prio_queue[i][0].pop(), i


def DetermineLowest(prio_queue, prev_lowest):
    for n,i in enumerate(prio_queue[prev_lowest:]):#can depend on order since it's a list
        if len(i[0]) + len(i[1]) != 0:
            return n + prev_lowest
    return 0#no lowest found


def SolveManhatten(slider, target):
    target_dict = {i:(n%width, n//width) for n, i in enumerate(target)}

    queue = [([], [])]#will never have elements inserted
    for i in range(1, MaximumManhatten((width, height)) + 1):
        queue.append(([], []))
    queue[1] = ([slider], [])
    seen = set()
    if slider.current == target:
        return slider
    lowest = 1
    k = 0
    while t := PopPriorityQueue(queue, lowest):
        k += 1
        slider, p = t
        if len(queue[p][0]) == 0:
            queue[p] = (queue[p][1], queue[p][0])
            if len(queue[p][0]) == 0:
                lowest = DetermineLowest(queue, lowest)
        seen.add(slider.current)
        for i in slider.Neighbors():
            if i.current not in seen:
                if i.current == target:
                    #print(f'k: {k}')
                    return i
                seen.add(i.current)
                if (m := GetManhattenSum(i, target_dict)) < lowest:
                    lowest = m
                queue[m][1].append(i)
    return slider


#upper bound calculation for the sum of a slider's elements' Manhattan distances, it's higher than the actual theoretical but calculating the conversion coefficient is really slow and it gets smaller as the sliders get larger so I'll probably leave it at .8 since I doubt anything will have to be higher than that in the tests
def MaximumManhatten(dim):#if you wish to see my work on deriving this just email, it's several pages of scratch work, I figured this out by brute-forcing a lot and looking for patterns
    #works by finding the 1 X K max manhattan and in one step and then using that to find the max manhattan for N x K in one step
    #this is based off of the initial formula's being able to to find the max manhattan for 1 x K and the second ones condensing repeated addition used to advance down the Z x K series where Z is any integer smaller than or equal to K
    #dims will be N x K for comment purposes
    N, K = sorted(dim)#N x K and K x N have same max
    second_dif = K#2nd finite difference base number, will probably be multiplied by 2 later
    zero_first_dif = 0#0th index 1st finite difference compared to 0 x K, the same as the Maximum Manhattan for 1 x K
    if K % 2 == 0:#N is even
        zero_first_dif = K * K - (u := (K / 2)) * (u + 1)# part after - derived from sequence plugged into oeis.org, n(n-1), and some fiddling until it worked
    else:#K is odd
        zero_first_dif = K * K - ((K + 1) / 2)**2

    def f(Z):#the number of times to multiply by K when in sequence location Z x number>=Z to adjust the output of below to adjust for a growing sequence
        x = Z - 1
        return x * (x + 1) / 2 + math.floor((x + 1) ** 2 / 4)#from oeis.org after manually calculating this for about 10 sequence positions without it

    return int(zero_first_dif * N + f(N) * K * .8) + 1#the .8 and +1 comes from experimental testing showing that the actual maximum manhattan distance being at most .8 of this number, baring 2x2 but those are small enough I don't care since I won't be using them


#args = ['12345678_']
#args = ['8672543_1']#31 length to solution

width, height = -1,-1


import time

def RunOne():
    s = Slider(args[0])
    if len(args) == 2:
        if args[0] == args[1]:
            return s, s

    if not GenericSolvable(s, args[1]):  # checks if solvable if given only the starting condition
        return s, None

    ns = SolveManhatten(s, args[1])
    return s, ns


def EckelRun(filename):
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

        ns = SolveManhatten(s, target)

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
    print(len(runs))


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
    print(len(runs))



def main():
    global args
    global width, height
    args = ['eckel.txt']
    width, height = 4,4
    GenerateNeighborLUT()

    #Bench3x3(Solve)
    #Bench4x4(Solve)
    #Bench3x3(SolveManhatten)
    #Bench4x4(SolveManhatten)
    #exit()
    if len(args) != 0:
        if len(args) == 1:
            if '.' not in args[0]:
                args.append(''.join(sorted(args[0].replace('_', ''))) + '_')
            else:
                EckelRun(args[0])
                exit()
        width, height = GetDimensions(args[0])

        t0 = time.time()
        s, ns = RunOne()

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
        string = 'Version: 1.2\t'#Manhattan speedup is significant enough I think it is worth making this version 2
        runs = []

        for i in range(500):
            args = [GenerateRandom3x3(), '12345678_']
            t0 = time.time()
            s, ns = RunOne()
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