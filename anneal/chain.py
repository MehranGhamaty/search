#/bin/python3.6
"""
    This is a pseudo markov chain class
"""

import numpy as np

def equals(epsilon):
    """ equality within a certain margin of error """
    def equal(obj0, obj1):
        """ return me so I can be called without needing to add epsilon later """
        return abs(obj0-obj1) < epsilon
    return equal

class MarkovChain(object): #pylint: disable=too-few-public-methods
    """
        This class has a list of states and
        a probability for picking the state
    """
    def __init__(self, states):
        self.__chain = [1/len(states)] * len(states)
        self.__accepted = [0] * len(states) #do this to sort of normalize
        self.__picked = [0] * len(states)
        #but really its so we don't have to worry about /0
        self.__states = states
        self.__lastchange = None

    def __validate(self):
        percent = 0
        maxloc, maxval = (-1, -np.inf)
        for i, val in enumerate(self.__chain):
            if val < 0:
                self.__chain[i] = 0
            else:
                percent += val
                if val > maxval:
                    maxloc, maxval = i, val

        if percent > 1:
            self.__chain[maxloc] -= (percent-1)



    def __updatechain(self, j):
        orig = self.__chain[j]
        self.__chain[j] = self.__accepted[j] / self.__picked[j]
        diff = (orig - self.__chain[j]) / (len(self.__chain)-1)
        for i in range(len(self.__chain)):
            if i == j:
                continue
            self.__chain[i] += diff
        self.__validate()
        print("chain looks like, ", self.__chain)
        print("accpeted looks like, ", self.__accepted)
        print("picked looks like, ", self.__picked)

    def __call__(self, observation):
        #call one of states on observation with probability according to chain
        j = np.random.choice(range(len(self.__chain)), p=self.__chain)
        self.__picked[j] += 1
        self.__updatechain(j)
        value = self.__states[j](observation)
        self.__lastchange = j
        return value

    def __repr__(self):
        rep = "{}:\n".format(self.__class__.__name__)
        for i in range(len(self.__chain)):
            rep += "{} : {}\n".format(self.__states[i], self.__chain[i])
        return rep

    def accept(self):
        """ inform the chain that we accepted j """
        self.__accepted[self.__lastchange] += 1
        self.__updatechain(self.__lastchange)
