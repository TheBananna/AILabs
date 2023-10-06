import sys;args = sys.argv[1:]
# Nicholas Bonanno, pd. 6
import math, random
def ProcessArgs():
    global args, weights, transfer_function, heights, transfer_function_derivative, training_data
    training_data = [[list(map(int, string.replace('\n', '').split(' => ')[0].split(' '))) + [1], [int(string.replace('\n', '').split(' => ')[1])]] for string in open(args[0], 'r').readlines()]
    heights = [training_data[0][0].__len__(), 4, 3, 2, 1]#inputs to account for bias, 2, 1, output
    weights = [[random.random() for j in range(heights[i] * heights[i+1])] for i in range(len(heights) - 1)]
    #print(weights)
    #if weights[0].__len__() == 0:
    #    weights.remove(weights[0])
    transfer_function = lambda x : 1/(1+math.exp(-x))
    transfer_function_derivative = lambda x : x*(1-x)#x is the logistic function output as y was already put through it so this is y(1-y)

    # heights = [len(inputs)]
    # height = len(inputs)
    # for i in weights:
    #     heights.append(len(i) // height)
    #     height = len(i) // height
    # heights[len(heights) - 1] = len(weights[len(weights) - 1])
    new_weights = []
    for i in range(len(weights) - 1):
        weight_matrix = []
        weight_list = weights[i]
        for j in range(heights[i+1]):
            weight_matrix.append(weight_list[j * heights[i] : (j+1) * heights[i]])
        new_weights.append(weight_matrix)
    new_weights.append([weights[len(weights) - 1]])
    new_weights.insert(0, [])
    weights = new_weights#format [[], [[WEIGHT for previous layer height], [...], [...], ... for this layer height], [...], [...], ... for layer count]
    #index 0 is empty as the input has no weights as it's just directly set


def dot_product(l1, l2):#make it take iterators and not just lists
    return sum(l1[i] * l2[i] for i in range(len(l1)))


def CalculatePartialYErrors(layers, weights, training_data):#calculated partial E / partial y NOT the weight errors
    global heights, transfer_function_derivative
    layer_errors = [[0.0] * i for i in heights]#negative gradient so no need to negate
    layer_errors[len(layer_errors) - 1] = [training_data[i] - layers[len(layers) - 1][i] for i in range(heights[len(heights) - 1])]#make sure training data and layer orientation are the same and not flipped
    for L in range(len(layers) - 2, -1, -1):#start, end (exclusive), increment
        for j in range(heights[L]):
            layer_errors[L][j] = dot_product(layer_errors[L+1], list(weights[L+1][k][j] for k in range(heights[L+1]))) * transfer_function_derivative(layers[L][j])
        #layer_errors[L] = [dot_product(layer_errors[L+1], list(weights[L+1][k][j] for k in range(heights[L+1]))) * transfer_function_derivative(layers[L][j]) for j in range(heights[L])]
    return layer_errors


def GetWeightErrors(y_errors, layers, weights):#these will also not be adjusted by alpha
    global heights
    weight_errors = [[[0.0 for j in range(len(weights[L][i]))] for i in range(len(weights[L]))] for L in range(len(weights))]
    for L in range(1, len(weight_errors)):
        for i in range(heights[L]):
            weight_errors[L][i] = [layers[L-1][j] * y_errors[L][i] for j in range(heights[L-1])]
            #weight_errors[L][j] = [(layers[L][i]) * y_errors[L+1][j] for i in range(len(weights[L][j]))]
    return weight_errors


ALPHA = 1
def GetAdjustedWeights(weights, weight_errors):
    return [[[weights[L][i][j] + ALPHA * weight_errors[L][i][j] for j in range(len(weights[L][i]))] for i in range(len(weights[L]))] for L in range(len(weights))]


def EvaluateNN(weights, inputs):#return whole network so I can use it for gradient descent
    global heights
    layers = [[0.0] * i for i in heights]
    layers[0] = [i for i in inputs]
    for i in range(1, len(layers) - 1):
        for j in range(heights[i]):
            layers[i][j] = transfer_function(dot_product(weights[i][j], layers[i - 1]))
    #final step as these weights only go their output node
    for i in range(len(layers[len(layers) - 1])):
        layers[len(layers) - 1][i] = (layers[len(layers) - 2][i] * weights[len(layers) - 1][i][0])
    return layers


def TrainOne(weights, training_data):#trains one epoch
    errors = []
    for training in training_data:
        layers = EvaluateNN(weights, training[0])
        y_errors = CalculatePartialYErrors(layers, weights, training[1])
        weight_errors = GetWeightErrors(y_errors, layers, weights)
        weights = GetAdjustedWeights(weights, weight_errors)
        #errors.append(.5*sum(y_errors[len(y_errors) - 1][i]**2 for i in range(len(y_errors[len(y_errors) - 1]))))
        errors.append(abs(y_errors[len(y_errors) - 1][0]**2))
    return weights, (1/len(errors))*sum(errors)


def PrintWeights(weights):
    output = ''
    for layer in weights[1:]:
        output = f"{output}{', '.join(', '.join(map(str, height)) for height in layer)}\n"
    print(output)


def main():
    global args, weights, transfer_function, heights, training_data, ALPHA
    if not args:
        args = ['weightsNN2.txt']
    #random.seed(0)
    ProcessArgs()
    #print(weights)
    #print(heights)
    #exit()
    print(f"Layer counts: {' '.join(map(str, heights))}")
    error = 1
    print(weights)
    epoch = 0
    ALPHA = 1
    while epoch < 100000:
        weights, error = TrainOne(weights, training_data)
        if epoch % 3000 == 0 and error > .2:
            ProcessArgs()
            ALPHA = 1
        if epoch % 1000 == 0:
            if epoch % 10000 == 0:
                ALPHA = max(.01, ALPHA - .05 * ALPHA)
            PrintWeights(weights)
            print(error)
        epoch += 1
    #print('')
    #TrainOne(weights, training_data)
    for training in training_data:
        print(EvaluateNN(weights, training[0]))
    #print(error)
    breakpoint()
    return error





if __name__ == '__main__':
    main()



