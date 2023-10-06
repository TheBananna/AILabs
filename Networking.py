import sys;args = sys.argv[1:]
# Nicholas Bonanno, pd. 6
import random

def ProcessArgs(args):
    global node_count, average_connections, type_of_connect
    node_count = int(args[2])
    average_connections = float(args[0])
    type_of_connect = args[1]


def Classical():#each node has a random chance to be connected to any other node
    global node_count, average_connections, type_of_connect
    nodes = [(i, set()) for i in range(node_count)]
    for i in range(round(node_count * average_connections) // 2):
        node1 = random.choice(nodes)
        node2 = random.choice(nodes)
        while node2 == node1 or node2[0] in node1[1]:
            node2 = random.choice(nodes)
        node1[1].add(node2[0])
        node2[1].add(node1[0])
    return nodes



def Iterative():#nodes with more connections are more likely to get even more connections
    #use random.choices or with a weight list or random.choice on a list that has a node added for every connection that is added to it
    global node_count, average_connections, type_of_connect
    nodes = [[i, set()] for i in range(node_count)]
    node_choices = [] + [nodes[0]] * (node_count - 1)
    for node in nodes[1:]:
        node[1].add(0)
        nodes[0][1].add(node[0])
        node_choices.append(node)
    total_connections = node_count * average_connections
    while len(node_choices) < total_connections:
        #print(i)
        node1, node2 = random.choices(node_choices, k=2)
        while node1[0] == node2[0] or node2[0] in node1[1]:
            node1, node2 = random.choices(node_choices, k=2)
        node1[1].add(node2[0])
        node2[1].add(node1[0])
        node_choices.append(node1)
        node_choices.append(node2)
    return nodes

import time
def main():
    global type_of_connect, args, node_count, average_connections
    start = time.time()
    DEBUG = False
    if not args:
        DEBUG = True
        args = [f'5.33', 'i', '500000']
        args = ['24.8', 'i', '10600']
    ProcessArgs(args)
    if type_of_connect.lower() == 'c':
        nodes = Classical()
    else:
        nodes = Iterative()
    degrees = dict()
    for node in nodes:
        if len(node[1]) not in degrees:
            degrees[len(node[1])] = 0
        degrees[len(node[1])] += 1
    output = ''
    for degree, count in sorted(list(degrees.items())):
        output = f'{output} {degree}:{count}'
    print(output)
    print(time.time() - start)
    if DEBUG:
        print(sum(len(i[1]) for i in nodes))
        print(5.33*500000)



if __name__ == '__main__':
    main()
