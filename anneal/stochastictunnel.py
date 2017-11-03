#/bin/python3.6

"""
    provides stochastic tunneling
"""

import numpy as np

def stochastictunnel(fun, minf, gamma, tunnelingfunc=0):
    """ returns a modifed function """
    def tunnelfunc(datum):
        """ tunnels the function """
        if tunnelingfunc == 0:
            #print(fun(datum))
            #print(-(fun(datum)-minf) / gamma)
            return fun(datum)*(1-np.exp(-(fun(datum)-minf)/ gamma))
        elif tunnelingfunc == 1:
            return fun(datum)*(1-np.exp(-gamma*(fun(datum)-minf)))
        elif tunnelingfunc == 2:
            return fun(datum)*(np.tanh(-gamma*(fun(datum)-minf)))
        elif tunnelingfunc == 3:
            return fun(datum)*(np.sinh(-gamma*(fun(datum)-minf)))


    return tunnelfunc
