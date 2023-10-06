import sys;
args = sys.argv[1:]
#Nicholas Bonanno, pd. 6

if len(args) == 0:#for running on my computer
    args = ['words.txt']


class Node(object):
    def __init__(self, word):
        self.word = word
        self.neighbors = set()
        self.path = []
        self.distance = 0

    def __str__(self):
        return f'{self.distance}'# : {list(self[1])}'


#r = [0,1,2,3,4,5]
def letter_match(word1, word2):
    if word1 == word2:#not sure why I need this but Nodes reference themselves if I don't
        return False
    return (word1[0] == word2[0]) + (word1[1] == word2[1]) + (word1[2] == word2[2]) + (word1[3] == word2[3]) + (word1[4] == word2[4]) + (word1[5] == word2[5]) == 5


def get_node(word, seen):
    val = seen.get(word)
    if val is not None:
        return val
    else:
        n = (word, set(), [], 0)#replace set with dict with word as key so I can use a tuple
        seen[word] = n
        return n


def GenerateGraphsDict(words):#many small graphs not connected
    seen = dict()
    get_node_loc = get_node
    root = get_node_loc(words[0], seen)
    pos = 0
    for i in words:
        pos += 1
        node = get_node_loc(i, seen)
        for j in words[pos:]:#only need to check the elements in front of this one as the ones behind it have already compared
            comp = get_node_loc(j, seen)
            if letter_match(i, j):
                node[1].add(comp)#these are sets so I don't need to check if comp/node is already there
                comp[1].add(node)
    return seen


def RecursiveAdd(top, data):
    data.add(top)
    for i in top[1]:
        if i not in data:
            RecursiveAdd(i, data)


def DeclutterGraphs(graphs):
    ret = set()
    sub = set()
    for i in graphs:
        if i not in sub:
            ret.add(i)
            for j in i[1]:
                RecursiveAdd(j, sub)
    return ret


def RecursiveEdges(root, data):
    edges = 0
    data.add(root)
    for i in root[1]:#so edges aren't double counted
        if i not in data:
            edges += 1
            edges += RecursiveEdges(i, data)
    return edges


def EdgeCount(dec):
    edges = 0
    seen = set()
    for i in dec:
        edges += RecursiveEdges(i, seen)
    return edges


def EdgeCountNew(graphs):
    seen = set()
    edges = 0
    for i in graphs:
        for j in i[1]:
            if j not in seen:
                edges += 1
        seen.add(i)
    return edges


def GroupComponentEdges(graphs):
    degrees = dict()
    for i in graphs:
        edges = RecursiveEdges(i, set())
        if edges not in degrees:
            degrees[edges] = set()
        degrees[edges].add(i)
    return degrees


def DegreeList(graphs):#do not use dec on this
    degrees = []
    for i in graphs:
        if len(i[1]) > len(degrees) - 1:
            degrees.extend(set() for i in range(len(i[1]) - (len(degrees) - 1)))
            degrees[len(i[1])] = set()
        degrees[len(i[1])].add(i)
    return degrees


def RecursiveSize(root, data):
    size = 1
    data.add(root)
    for i in root[1]:
        if i not in data:
            size += RecursiveSize(i, data)
    return size


def SizeDict(dec):#should use dec
    sizes = dict()
    for i in dec:
        sizes[i] = RecursiveSize(i, set())
    return sizes


def IsComplete(root, size):
    if len(root[1]) != size - 1:
        return False
    for i in root[1]:#need to ensure all nodes touch and that their neighbors match root's
        if len(i[1]) != size - 1:#to improve performance in the likely i's neighbor size makes this not complete, no set difference required
            return False
        if len(i[1].difference(root[1])) != 1:
            return False
    return True#if not false yet, then the graph should be complete


#sorry for the horrifically long variable name
def CompleteGraphCountDict(size_dict):#return a dictionary with n as key and number of them as value
    complete_graph_count_dict = dict()
    for i, j in size_dict.items():
        #breakpoint()
        if 2 <= j <= 4 and IsComplete(i, j):#2 <= j <= 4 is because I only need K2, K3, and K4
            if j not in complete_graph_count_dict:
                complete_graph_count_dict[j] = 0
            complete_graph_count_dict[j] += 1
    return complete_graph_count_dict


def FarthestNode(root):
    queue = [root]
    next_queue = []
    seen = set()
    node = None
    #farthest = root
    while len(queue) > 0 or len(next_queue) > 0:
        if len(queue) == 0:
            temp = queue
            queue = next_queue
            next_queue = temp
            next_queue.clear()
        node = queue.pop()
        seen.add(node)
        #if node[3] > farthest[3]:
            #farthest = node
        for i in node[1]:
            if i not in seen:
                #i[3] = node[3] + 1
                next_queue.append(i)
                seen.add(i)
    return node


def ShortestPath(root, target):#bfs breadth first search
    queue = [root]
    next_queue = []
    seen = set()
    while len(queue) > 0 or len(next_queue) > 0:
        if len(queue) == 0:
            temp = queue
            queue = next_queue
            next_queue = temp
            next_queue.clear()
        node = queue.pop()
        seen.add(node)
        for i in node[1]:
            if i not in seen:
                i[2] = node[2].copy()
                next_queue.append(i)
                seen.add(i)
                i[2].append(node)
                if i == target:
                    i[2].append(i)
                    return i[2]

    return ['NO_PATH_FOUND']


def GroupComponentSizes(size_dict):
    ret = set()
    for i, j in size_dict.items():
        if j not in ret:
            ret.add(j)
    return ret


def TakeFirstFrom(list, index):
    for i in range(index, len(list)):
        if len(list[i]) > 0:
            return list[i].__iter__().__next__()
    return None


def DEBUG_BFS_SEARCH(word1, word2):
    queue = [word1]
    seen = set()

    while queue:
        node = queue.pop()
        seen.add(node)
        for i in node[1]:
            if i not in seen:
                if i == word2:
                    return True
                queue.append(i)
    return False


def exercises_1_4():
    print(f'Word count: {len(graphs)}')
    print(f'Edge count: {EdgeCountNew(graphs)}')
    print(f'Degree list: ' + ' '.join([str(len(i)) for i in degree_list]))


def exercises_5_13():
    word1 = args[1]
    word2 = args[2]
    component_edge_groups = GroupComponentEdges(dec)
    size_dict = SizeDict(dec)
    complete_graph_count_dict = CompleteGraphCountDict(size_dict)
    component_size_groups = GroupComponentSizes(size_dict)


    print(f'Second degree word: {TakeFirstFrom(list(reversed(degree_list)), 1)}')#5
    print(f'Connected component size count: {len(component_size_groups)}')#6
    print(f'Largest component size: {max(size_dict.values())}')#7
    #breakpoint()
    print(f'K2 count: {complete_graph_count_dict[2]}')#8
    print(f'K3 count: {complete_graph_count_dict[3] if 3 in complete_graph_count_dict else 0}')#9
    print(f'K4 count: {complete_graph_count_dict[4] if 4 in complete_graph_count_dict else 0}')#10
    print('Neighbors: ' + ' '.join([i[0] for i in graphs_dict[word1][1]]))#11
    print(f'Farthest: {FarthestNode(graphs_dict[word1])[0]}')#12
    print(f'Path: '+ ' '.join(map(str, ShortestPath(graphs_dict[word1], graphs_dict[word2]))))#13


#not method code
import time
t0 = time.time()


#args.append('locked')
#args.append('blinks')
#args.append('hating')
#args.append('severs')

words = open(args[0], 'r').read().splitlines()
graphs_dict = GenerateGraphsDict(words)
graphs = graphs_dict.values()
dec = DeclutterGraphs(graphs)
degree_list = DegreeList(graphs)

if len(args) == 1:
    exercises_1_4()
else:
    exercises_5_13()

tf = time.time()
print(f'\nConstruction time: ' + f'{tf - t0}'[0:4] + 's')