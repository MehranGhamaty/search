"""
    plotter class
"""

import matplotlib.pyplot as plt

class Plotter:
    """
        basic plotting function for updating a graph easily
    """
    def __init__(self, axis, scorefunc, titletext):
        self.axis = axis
        self.xaxis = []
        self.yaxis = [[] for _ in scorefunc]
        self.scorefunc = scorefunc
        self.titletext = titletext

    def __call__(self, new):
        self.axis.clear()
        if callable(self.titletext):
            self.axis.set_title(self.titletext(new))
        else:
            self.axis.set_title(self.titletext)
        plthandles = []
        if self.xaxis:
            self.xaxis.append(self.xaxis[-1]+1)
        else:
            self.xaxis.append(0)
        for i, scorekey in enumerate(self.scorefunc):
            self.yaxis[i].append(self.scorefunc[scorekey](new))
            plthandles.append(self.axis.plot(self.xaxis, self.yaxis[i], label=scorekey)[0])
        self.axis.legend(plthandles, title="tests")

        plt.draw()
        plt.pause(0.00001)

    def setscorefunc(self, key, newsc):
        """ sets the score function """
        self.scorefunc[key] = newsc
    def settitle(self, title):
        """ sets the title """
        self.titletext = title
