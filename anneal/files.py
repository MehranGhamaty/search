#!/bin/python3.6

"""
    helper functions for handling file IO

"""

import graph as g


def readparams(filename):
    """
        reads in parameter file
        INITPROB #
        FREEZE_LIM #
        SIZEFACTOR #
        CUTOFF #
        TEMPFACTOR #
        MINPERCENT #
        GAMMA #
    """
    params = {}
    def updatetmp(factor):
        """ just a function for updating """
        def update(temp):
            """ change temp by factor """
            return temp*factor
        return update
    def findgamma(curre, mine):
        """ calculates gamma, not very good set between 1-5 works better """
        print("e-mine", curre-mine)
        gam = (curre-mine)/0.05
        return gam if gam != 0 else 1

    with open(filename, 'r') as filehandle:
        for line in filehandle:
            contents = line.split()
            if not contents:
                continue
            if contents[0] == "INITPROB":
                params[contents[0].lower()] = float(contents[1])
            elif contents[0] == "FREEZE_LIM":
                params["freezelimit"] = int(contents[1])
            elif contents[0] == "SIZEFACTOR":
                params[contents[0].lower()] = int(contents[1])
            elif contents[0] == "CUTOFF":
                params[contents[0].lower()] = float(contents[1])
            elif contents[0] == "TEMPFACTOR":
                params["temperatureupdate"] = updatetmp(float(contents[1]))
            elif contents[0] == "MINPERCENT":
                params[contents[0].lower()] = float(contents[1])
            elif contents[0] == "GAMMA":
                if contents[1].replace('.', '', 1).isdigit():
                    params[contents[0].lower()] = float(contents[1])
                else:
                    params[contents[0].lower()] = findgamma

    params["upperbound"] = lambda x: 1
    return params

def readgraph(filename):
    """
        input a filename

        The file format is the following:
            c COMMENT LINE
            p FORMAT NODES EDGES
                FORMAT (string) -> "edge"
                NODES (int) -> n nodes
                EDGES (int) -> m edges
            n ID VALUE
            e W V
            d DIM METRIC
                DIM (int) -> number of dimensions
                METRIC (string) -> LX where X is the norm you are taking
                or LINF for inf norm, can have a suffix of S to denote
                not taking the square (reduces computation and sensitivity)
            v X1 X2 X3 ... XD
                must come after 'd'
            p PARAM VALUE
                PARAM (string) -> "MINLENGTH" or "MAXLENGTH"
                VALUE (numeric) -> value of param

        More specifics of this format can be found at
        http://www.stasbusygin.org/writings/ccformat.pdf

        returns a graph object
    """
    graphtoreturn = g.Graph()
    with open(filename, 'r') as filehandle:
        for line in filehandle:
            contents = line.split()
            if not contents:
                continue
            if contents[0] == 'c':
                pass
            elif contents[0] == 'p':
                pass
            elif contents[0] == 'n':
                graphtoreturn.addvertex(contents[1], contents[2])
            elif contents[0] == 'e':
                graphtoreturn.addundirectededge(contents[1], contents[2])
            elif contents[0] == 'd':
                graphtoreturn.setmetric(contents[1], contents[2])
            elif contents[0] == 'v':
                #make sure this follows d
                graphtoreturn.setembedding(contents[1], contents)
            elif contents[0] == 'x':
                pass
    return graphtoreturn


def outputcoloringsolution(solutiongraph, filename):
    """
        outputs solution to coloring in Clique and Coloring Graph Problems Format
    """
    with open(filename, 'w') as filehandle:
        coloring = solutiongraph.getvaluedict()
        filehandle.write("s col {}\n".format(len(coloring)))
        for color, vertices in coloring.items():
            for vertex in vertices:
                filehandle.write("l {} {}\n".format(vertex, color))

def outputhistory(history, initialobjective, filename):
    """ write the history to a file """
    with open(filename, 'w') as filehandle:
        filehandle.write(str(initialobjective)+"\n")
        for line in history:
            filehandle.write("{} {}\n".format(line[0], line[1]))
