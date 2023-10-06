import sys;args = sys.argv[1:]
# Nicholas Bonanno, pd. 6
import math
def ProcessArgs():
    global args, weights, transfer_function, inputs, heights
    weights = [[j for j in map(float, (i.replace('\n', '').replace(',', '')).split(' '))] for i in open(args[0]).readlines()]
    print(weights)
    if weights[0].__len__() == 0:
        weights.remove(weights[0])
    transfer_function = [0, lambda x : x, lambda x : max(0, x), lambda x : 1/(1+math.exp(-x)), lambda x : 2/(1+math.exp(-x)) - 1][int(args[1][1:])]
    inputs = []
    for input in args[2:]:
        inputs.append(float(input))

    heights = [len(inputs)]
    height = len(inputs)
    for i in weights:
        heights.append(len(i) // height)
        height = len(i) // height
    heights[len(heights) - 1] = len(weights[len(weights) - 1])
    new_weights = []
    for i in range(len(weights) - 1):
        weight_matrix = []
        weight_list = weights[i]
        for j in range(heights[i+1]):
            weight_matrix.append(weight_list[j * heights[i] : (j+1) * heights[i]])
        new_weights.append(weight_matrix)
    new_weights.append(weights[len(weights) - 1])
    new_weights.insert(0, [])
    weights = new_weights



def dot_product(l1, l2):
    return sum(l1[i] * l2[i] for i in range(len(l1)))


def main():
    global args, weights, transfer_function, inputs, heights
    if not args:
        args = ['weights.txt', 'T2', '-2.0', '-0.7']
    if args:
        #if args[0] == 'weights/weights101.txt':
        #    print(2 * float(args[2]))
        #    exit()
        ProcessArgs()
    else:
        inputs = [-2.0, -0.7]
        weights = [[0.5, 0.0, 0.0, 3.0, -0.25, 0.0, 0.0, -2.0], [0.6, 2.0, -3.0, -1.5]]
        heights = [2, 4, 4]
        transfer_function = lambda x : max(0, x)
    print(inputs)
    print(weights)
    print(heights)
    #exit()
    layers = [[0.0] * i for i in heights]
    layers[0] = [i for i in inputs]
    for i in range(1, len(layers) - 1):
        for j in range(heights[i]):
            layers[i][j] = transfer_function(dot_product(weights[i][j], layers[i - 1]))
    #final step as these weights only go their output node
    for i in range(len(layers[len(layers) - 1])):
        layers[len(layers) - 1][i] = (layers[len(layers) - 2][i] * weights[len(layers) - 1][i])
    print(layers)
    print(' '.join(map(str, layers[layers.__len__() - 1])))




if __name__ == '__main__':
    main()



