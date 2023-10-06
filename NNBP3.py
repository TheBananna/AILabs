import sys;args = sys.argv[1:]
# Nicholas Bonanno, pd. 6
import math, random
def ProcessArgs():
    global args, weights, transfer_function, heights, transfer_function_derivative, training_data, inequality, radius_squared
    inequality = args[1][0:2] if args[1][1] == '=' else args[1][0]
    radius_squared = float(args[1][len(inequality):])
    inequality = {'<':0, '<=':1, '>':.2, '>=':3}[inequality]
    weights = [[j for j in map(float, (i.replace('\n', '').replace(',', '')).split(' '))] for i in open(args[0]).readlines()[1:]]#skip first line as it is a comment, there may be more on later tests but I will deal with that later if needed
    #print(weights)
    if weights[0].__len__() == 0:
        weights.remove(weights[0])
    heights = []#first is inputs + bias and last is output

    transfer_function = lambda x : 1/(1+math.exp(-x))
    transfer_function_derivative = lambda x : x*(1-x)#x is the logistic function output as y was already put through it so this is y(1-y)

    heights = [2]
    height = 2
    for i in weights:
        heights.append(len(i) // height)
        height = len(i) // height
    heights[len(heights) - 1] = len(weights[len(weights) - 1])
    new_weights = []
    for i in range(len(weights) - 1):
        weight_matrix = []
        weight_list = weights[i]
        for j in range(heights[i + 1]):
            weight_matrix.append(weight_list[j * heights[i]: (j + 1) * heights[i]])
        new_weights.append(weight_matrix)
    new_weights.append([weights[len(weights) - 1]])
    new_weights.insert(0, [])
    weights = new_weights#format [[], [[WEIGHT for previous layer height], [...], [...], ... for this layer height], [...], [...], ... for layer count]
    #index 0 is empty as the input has no weights as it's just directly set


def training_data():
    global inequality, radius_squared
    x = random.random() * 3 - 1.5
    y = random.random() * 3 - 1.5
    dist = x*x+y*y
    if inequality == 0:
        out = dist < radius_squared
    elif inequality == 1:
        out = dist <= radius_squared
    elif inequality == 2:
        out = dist > radius_squared
    else:
        out = dist >= radius_squared
    return [[x, y, 1], [int(out)]]


def dot_product(l1, l2):#make it take iterators and not just lists
    return sum(l1[i] * l2[i] for i in range(len(l1)))


def CalculatePartialYErrors(layers, weights, training_data):#calculated partial E / partial y NOT the weight errors
    global heights, transfer_function_derivative
    layer_errors = [[0.0] * i for i in heights]#negative gradient so no need to negate
    layer_errors[len(layer_errors) - 1] = [(training_data[i] - layers[len(layers) - 1][i]) for i in range(heights[len(heights) - 1])]#make sure training data and layer orientation are the same and not flipped
    for L in range(len(layers) - 2, -1, -1):#start, end (exclusive), increment
        for j in range(heights[L]):
            layer_errors[L][j] = dot_product(layer_errors[L+1], list(weights[L+1][k][j] for k in range(heights[L+1]))) * transfer_function_derivative(layers[L][j])
        #layer_errors[L] = [dot_product(layer_errors[L+1], list(weights[L+1][k][j] for k in range(heights[L+1]))) * transfer_function_derivative(layers[L][j]) for j in range(heights[L])]
    return layer_errors


def GetWeightErrors(y_errors, layers, weights, adjust=1.0):#these will also not be adjusted by alpha
    global heights
    weight_errors = [[[0.0 for j in range(len(weights[L][i]))] for i in range(len(weights[L]))] for L in range(len(weights))]
    for L in range(1, len(weight_errors)):
        for i in range(heights[L]):
            weight_errors[L][i] = [layers[L-1][j] * y_errors[L][i] * adjust for j in range(heights[L-1])]
            #weight_errors[L][j] = [(layers[L][i]) * y_errors[L+1][j] for i in range(len(weights[L][j]))]
    return weight_errors


ALPHA = 1
def GetAdjustedWeights(weights, weight_errors, error):
    return [[[weights[L][i][j] + ALPHA * weight_errors[L][i][j] for j in range(len(weights[L][i]))] for i in range(len(weights[L]))] for L in range(len(weights))]


def EvaluateNN(weights, inputs):#return whole network so I can use it for gradient descent
    global heights
    layers = [[0.0] * i for i in map(len, weights)]
    layers[0] = [i for i in inputs]
    for i in range(1, len(layers) - 1):
        for j in range(heights[i]):
            layers[i][j] = transfer_function(dot_product(weights[i][j], layers[i - 1]))
    #final step as these weights only go their output node
    for i in range(len(layers[len(layers) - 1])):
        layers[len(layers) - 1][i] = (layers[len(layers) - 2][i] * weights[len(layers) - 1][i][0])
    return layers


def TrainOne(weights, training_data, iterations=100):#trains one epoch
    errors = []
    weight_errors = []
    for i in range(iterations):
        training = training_data()
        layers = EvaluateNN(weights, training[0])
        y_errors = CalculatePartialYErrors(layers, weights, training[1])
        weight_errors.append(GetWeightErrors(y_errors, layers, weights, 1/iterations))
        #weights = GetAdjustedWeights(weights, weight_errors)
        #errors.append(.5*sum(y_errors[len(y_errors) - 1][i]**2 for i in range(len(y_errors[len(y_errors) - 1]))))
        errors.append(abs(y_errors[len(y_errors) - 1][0]))
    weights_error = [[[sum(weight_errors[k][L][i][j] for k in range(iterations)) for j in range(len(weights[L][i]))] for i in range(len(weights[L]))] for L in range(len(weights))]
    #gradient_magnitude = sum(sum(sum(abs(weights_error[L][i][j]) for j in range(len(weights_error[L][i]))) for i in range(len(weights[L]))) for L in range(len(weights)))
    weights = GetAdjustedWeights(weights, weights_error, sum(errors)/len(errors))
    return weights, sum(errors)/len(errors)


def PrintWeights(weights):
    output = ''
    for layer in weights[1:]:
        output = f"{output}{', '.join(', '.join(map(str, height)) for height in layer)}\n"
    print(output)


def GetCombinedWeightsPrint(weights):
    output = ''
    for n, layer in enumerate(weights[1:]):
        temp = f"{', '.join(', '.join(map(str, height)) for height in layer)}\n"

        output = f'{output}{temp}'
    return output


def PrintWeightsCombined(weights, final_weights):
    #output = GetWeightsPrint(weights)
    pass



def CombineWeights(weights, heights):#stacks a set of weights with no interconnect and adds a bias
    new_weights = [[]]
    for L in range(1, len(weights)):
        layer = []
        for i in range(len(weights[L])):
            layer.append([*weights[L][i]] + [0.0] * heights[L-1])
        for i in range(len(weights[L])):
            layer.append([0.0] * heights[L-1] + [*weights[L][i]])
        new_weights.append(layer)

    for i in range(len(new_weights[1])//2):
        new_weights[1][i] = [weights[1][i][0], 0, weights[1][i][1]]
    #new_weights[1][1] = [weights[1][1][0], 0, weights[1][1][1]]
    for i in range(len(new_weights[1])//2, len(new_weights[1])):
        new_weights[1][i] = [0, weights[1][i-len(new_weights[1])//2][0], weights[1][i-len(new_weights[1])//2][1]]
    #new_weights[1][3] = [0, weights[1][1][0], weights[1][1][1]]

    #new_weights[1][0][1] = 0.0
    #new_weights[1][1][1] = 0.0
    #new_weights[1][2][0] = 0.0
    #new_weights[1][3][0] = 0.0
    return new_weights



import time
def main():
    global args, weights, transfer_function, heights, training_data, ALPHA, DEBUG
    DEBUG = False
    if not args:
        args = ['NNBP3Weights.txt','x*x+y*y>1.3']
        DEBUG = True
    random.seed(0)
    args[1] = args[1][7:]
    ProcessArgs()
    print(heights)
    PrintWeights(weights)
    print('Layer counts: ' + ', '.join(map(str, [3] + [h * 2 for h in heights[1:len(heights) - 1]] + [1, 1])))
    orig_heights = heights
    heights = [3] + heights[1:]
    combined_weights = CombineWeights(weights, heights)
    heights = [3] + [h * 2 for h in orig_heights[1:len(orig_heights) - 1]] + [1, 1]
    last = combined_weights.pop()
    combined_weights.append([[last[0][0], last[1][1]]])
    combined_weights.append([[(1+math.e)/(2*math.e)]])
    PrintWeights(combined_weights)

    output = EvaluateNN(combined_weights, [1.5, 1.5, 1])
    print(output[len(output) - 1])
    #print(weights)
    #PrintWeights(weights)
    #print(CombineWeights(weights, heights))




if __name__ == '__main__':
    main()



