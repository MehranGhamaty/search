#/bin/python3.6

import random
import matplotlib.pyplot as plt
import numpy as np

class plotter:
    def __init__(self, ax, x, objfun):
        self.ax = ax
        self.x = x
        self.y = [*map(objfun, x)]
        self.objfun = objfun
        self.oldobjfun = []

    def __call__(self, currentpos):
        self.ax.clear()
        self.ax.hold(True)
        self.ax.plot(self.x,self.y)
        self.ax.plot([currentpos], [self.objfun(currentpos)], marker = 'o', markersize=30, color = "red")
#maybe plot all the old objectives in different  colors so it looks cool
        plt.draw()
        plt.pause(0.1)

    def setnewobjfun(self, objfun):
        self.y = [*map(objfun, x)]
        self.oldobjfun.append(self.objfun)
        self.objfun = objfun


if __name__ == "__main__":
    
    x = np.arange(-10,10,0.001)
    f = np.sin
    df = np.cos

    fig = plt.figure(1)
    ax = fig.add_subplot(1,1,1)

    p = plotter(ax,x,f)

    init = 0.2
    p(init)
    simulatedannealing(init,
        temperature=1000,
        temperatureupdate= lambda x : x*0.8,
        sizefactor=10,
        cutoff= 100,
        upperbound = lambda x : 50,
        objectivefunc = f,
        perturbator = lambda x : x-(random.random()*5)*df(x),
        ploton = p)


