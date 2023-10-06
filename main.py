# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.



#Version: 1.1	Time: 274.s		Time for impossible: 1.94s		# impossible: 258		Average path length: 16.8		Average time possible: 1.13s

class Slider:
    def __init__(self):
        self.current = ''
        self.slider_pos = ()
        self.previous = self
        #self.index = 0

    def SetCurrent(self, slider):
        self.current = slider
        self.slider_pos = ((i := slider.index('_')) % width, i // width)
        #self.index = self.slider_pos[1] * width + self.slider_pos[0]

    def Copy(self):
        s = Slider()
        s.previous = self
        return s

    def GetRows(self):
        string = []
        pos = 0
        for i in range(len(self.current) // height):
            string.append(self.current[pos:pos+width])
            pos += width
        return string

    def valid_coordinates(self, new_coords):
        return 0 <= new_coords[0] < width and 0 <= new_coords[1] < height


    def swap_chars(self, pos1, pos2, string):
        return f'{string[0:pos1]}{string[pos2]}{string[pos1 + 1:pos2]}{string[pos1]}{string[pos2 + 1:]}' if pos1 < pos2 else f'{string[0:pos2]}{string[pos1]}{string[pos2 + 1:pos1]}{string[pos2]}{string[pos1 + 1:]}'


    def swap_chars_slow(self, pos1, pos2, string):
        sl = [i for i in string]
        temp = sl[pos1]
        sl[pos1] = sl[pos2]
        sl[pos2] = temp
        return ''.join(sl)


    def IfValid(self, self_index, i, j):
        if self.valid_coordinates(c := (self.slider_pos[0] + i, self.slider_pos[1] + j)):
            s = self.Copy()
            s.slider_pos = c
            #s.index = c[1] * width + c[0]
            s.current = self.swap_chars(self_index, c[1] * width + c[0], self.current)
            return s
        return None


    def AddIfValid(self, neighbors, self_index, i, j):
        if self.valid_coordinates(c := (self.slider_pos[0] + i, self.slider_pos[1] + j)):
            s = self.Copy()
            s.slider_pos = c
            #s.index = c[1] * width + c[0]
            s.current = self.swap_chars(self_index, c[1] * width + c[0], self.current)
            neighbors.append(s)


    def Neighbors_old(self):
        self_index = self.slider_pos[1] * width + self.slider_pos[0]
        neighbors = []

        self.AddIfValid(neighbors, self_index, 0, 1)
        self.AddIfValid(neighbors, self_index, 0, -1)
        self.AddIfValid(neighbors, self_index, 1, 0)
        self.AddIfValid(neighbors, self_index, -1, 0)

        return neighbors


    def Neighbors(self):
        self_index = self.slider_pos[1] * width + self.slider_pos[0]

        return [
        self.IfValid(self_index, 0, 1),
        self.IfValid(self_index, 0, -1),
        self.IfValid(self_index, 1, 0),
        self.IfValid(self_index, -1, 0)
        ]


    def GetRow(self, row):
        return self.current[(p := height * row):p + width]


def GetManhattenSum(slider, target_dict):
    return sum(abs(n % width - target_dict[i][0]) + abs(n // width - target_dict[i][1]) for n,i in enumerate(slider.current))


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
    target_dict = {}
    for n,i in enumerate(target):
        target_dict[i] = n % width, n // width
    queue = [([], [])]#will never have elements inserted
    for i in range(1, MaximumManhatten((width, height)) + 1):
        queue.append(([], []))
    queue[1] = ([slider], [])
    seen = set()
    if slider.current == target:
        return slider
    lowest = 1
    while t := PopPriorityQueue(queue, lowest):
        slider, p = t
        if len(queue[p][0]) == 0:
            queue[p] = (queue[p][1], queue[p][0])
            if len(queue[p][0]) == 0:
                lowest = DetermineLowest(queue, lowest)
        seen.add(slider.current)
        for i in slider.Neighbors():
            if i is not None and i.current not in seen:
                if i.current == target:
                    return i
                seen.add(i.current)
                if (m := GetManhattenSum(i, target_dict)) < lowest:
                    lowest = m
                queue[m][1].append(i)
    return slider


#upper bound calculation for the sum of a slider's elements' Manhattan distances, it's higher than the actual theoretical but calculating the conversion coefficient is really slow so I'll probably leave it at .8 since I doubt anything will have to be higher than that in the tests
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


import Slider as sli, time, math

t0 = time.time()

width, height = 5,5
s = Slider()
temp = sli.GenerateRandomNxN(5)
s.SetCurrent(temp[0])
while not sli.GenericSolvable(s, temp[1]):
    temp = sli.GenerateRandomNxN(5)
    s.SetCurrent(temp[0])

ns = SolveManhatten(s, temp[1])
print(sli.GetString(ns))
print(f'Steps: {sli.GetPath(ns).__len__()}')
print(time.time() - t0)