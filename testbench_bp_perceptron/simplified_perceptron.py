import numpy as np


class Perceptron:

    def __init__(self, no_of_inputs, learning_rate=1):
        # save params
        self.learning_rate: int = learning_rate
        self.weights: np.array = np.zeros(no_of_inputs + 1, dtype=int)

    def predict(self, inputs):
        # compute sum(input[i]*weight[i]) + bias
        activation = np.dot(inputs, self.weights[1:]) + self.weights[0]
        # apply activation function
        return 1 if activation > 0 else 0

    def train(self, inputs, label):
        # predict using current weights
        prediction = self.predict(inputs)
        # update weights
        self.weights[1:] += self.learning_rate * (label - prediction) * inputs
        # update bias
        self.weights[0] += self.learning_rate * (label - prediction)


if __name__ == "__main__":

    """
        This is a simplified (for reasonable efficient hardware implementation), but fully-function implementation of 
        the perceptron algorithm.
        
        These simplification include:
            - binary classification
            - integer only datatype (instead of float)
            - single round training (no storage of training data, possibly single-cycle training)
            - single perceptron
            
            ToDo:
                - fixed integer bit width (and saturation instead of roll-over)
                - multiple perceptrons, choosen by lowest address bits
    """

    _NUM_ROUNDS = 5

    perceptron = Perceptron(no_of_inputs=2, learning_rate=1)

    # generate data for the logic OR function
    training_inputs = list()
    training_inputs.append(np.array([1, 1]))
    training_inputs.append(np.array([1, 0]))
    training_inputs.append(np.array([0, 1]))
    training_inputs.append(np.array([0, 0]))
    labels = np.array([1, 1, 1, 0])

    # train perceptron
    for _ in range(_NUM_ROUNDS):
        for inputs, label in zip(training_inputs, labels):
            perceptron.train(inputs, label)

    # check result
    for inputs, label in zip(training_inputs, labels):
        print("prediction for {}: expected: {}, actual: {}".format(inputs, label, perceptron.predict(inputs)))
