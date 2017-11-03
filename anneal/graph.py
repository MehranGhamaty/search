#/bin/python3.6
"""
    This is a collection of functions and a Graph class
"""

from queue import PriorityQueue
import copy
import numpy as np

class Graph:
    """
        graph is represented by a dictionary
        each element in dictionary has a key of id
        the key points to a list
        the first element in the list is the value
        the second element in the list is a list of vertices it connects to
        (if the edges have a weight we can make the second element
        a list of tuples (weight, vertex))
    """
    def __init__(self):
        """
            Initializes the used dictionaries and sets
            All dictionaries should share the same key
        """
        self.__graph = {}
        self.__embedding = {}
        self.__values = {}
        self.__metric = None

    def addvertex(self, identity, value=None):
        """ Adds a vertex to our graph """
        self.__graph[identity] = [value, []]

    def addedge(self, vertex0, vertex1):
        """
            Adds an edge from vertex0 to
            vertex1 to our our graph,
            if the vertices do not exist
            they are added
        """
        if not vertex0 in self.__graph:
            self.addvertex(vertex0)
        if not vertex1 in self.__graph:
            self.addvertex(vertex1)
        self.__graph[vertex0][1].append(vertex1)

    def addundirectededge(self, vertex0, vertex1):
        """
            Adds an edge from vetex0 to vertex1
            and an edge from vertex1 to vertex2
        """
        self.addedge(vertex0, vertex1)
        self.addedge(vertex1, vertex0)

    def setmetric(self, dimensions, metric):
        """
            Input: (int) dimensions, (string) metric

            Metric must be in form "LX" with an optional "S"
            at the end.

            X can be an integer or INF
        """
        self.__embedding = dict.fromkeys(self.__graph.keys(), [None] * dimensions)
        squaring = metric[-1] == "S"
        if squaring:
            power = int(metric[1:-1])
        else:
            power = int(metric[1:])

        def distance(target0, target1):
            """ calculate the distance between two points """
            dist = np.sum(np.abs(target0 - target1)**power)
            if not squaring:
                dist = np.sqrt(dist)
            return dist
        self.__metric = distance

    def setvalue(self, vertex, val):
        """ sets the value of vertex to val """
        ogval = self.__graph[vertex][0]
        if not ogval is None:
            self.__values[ogval].remove(vertex)
            #print("removing vertex {} from color {}".format(vertex, ogval))
            if not self.__values[ogval]:
                #print("{} is empty removing it".format(ogval))
                self.__values.pop(ogval)

        self.__graph[vertex][0] = val

        if val not in self.__values:
            #print("{} not in {}".format(val, self.__values))
            self.__values[val] = {vertex}
        else:
            self.__values[val].add(vertex)


    def setembedding(self, vertex, rep):
        """ sets the embedding of a vertex to rep"""
        self.__embedding[vertex] = rep

    def getgraph(self):
        """ returns the dictionary of the graph"""
        return self.__graph

    def getneighbors(self, vertex):
        """ returns list of neighbors """
        return self.__graph[vertex][1]

    def getvalue(self, vertex):
        """ returns value of vertex """
        return self.__graph[vertex][0]

    def getallwithvalue(self, value):
        """ returns a set of all vertices that have corresponding value """
        return self.__values[value]

    def getvaluedict(self):
        """ returns all values used """
        return self.__values

    def __repr__(self):
        edges = self.__graph
        colors = self.__values
        return "{}\nEdges:\n{}\nColors:\n{}\n".format(self.__class__.__name__, edges, colors)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

#so if I ever do the delta thing I can just remove the @createnew
def createnew(func):
    """
        decorator that makes a copy of the solution,
        so I can return a new instance for simulated annealing
    """
    def wrapper(solution):
        """ wrapper just makes a copy and runs the function on that copy """
        newsolution = copy.deepcopy(solution)
        func(newsolution)
        return newsolution
    return wrapper


@createnew
def kempe(solution):
    """
        0. assume we are at a valid coloring
        1. randomly pick a color
        2. get a vertex in that color
        3. choose a new color class for it
    """

    colors = solution.getvaluedict()
    swapping = set()
    pickedcolorset = set()
    newcolorset = set()
    #usedstart = {(color,vertex):set() for color, vertices in colors.items() for vertex in vertices}

    pickedvertex = None
    newcolor = None
    while not pickedvertex and not newcolor:

        pickedcolor = np.random.choice(list(colors.keys()))
        remainingvertices = solution.getallwithvalue(pickedcolor)
        pickedvertex = np.random.choice(list(remainingvertices))
        newcolor = np.random.choice(list(set(colors.keys()) - {pickedcolor}))

    print("picked vertex", pickedvertex, " newcolor ", newcolor)
    #everything in the newcolor set thats connected
    swapping = \
        set(solution.getneighbors(pickedvertex)).intersection(
            solution.getallwithvalue(newcolor))

    print("swapping", swapping)

    kempechain = set()
    #the new colorset + our picked vertex form the kempe chain
    front = {pickedvertex}.union(swapping)
    # we only want stuff from the classes we care about
    checkingsets = solution.getallwithvalue(pickedcolor).union(
        solution.getallwithvalue(newcolor))

    while kempechain.union(front) != kempechain:
        kempechain.update(front)
        tmpfront = copy.deepcopy(front)
        front.clear()
        for vertex in tmpfront:
            front.update(set(solution.getneighbors(vertex)).intersection(checkingsets))

    print("chain", kempechain)
    symmetricdiff = lambda x, y: (x - y).union(y - x)

    pickedcolorset = symmetricdiff(solution.getallwithvalue(pickedcolor), kempechain)
    newcolorset = symmetricdiff(solution.getallwithvalue(newcolor), kempechain)
    print("picked", pickedcolorset)
    print("new", newcolorset)

    for vertex in newcolorset:
        solution.setvalue(vertex, pickedcolor)
    for vertex in pickedcolorset:
        solution.setvalue(vertex, newcolor)
    return solution

@createnew
def fixedk(solution):
    """
        performs fixed-k

        We are given a number of partitions, we check for bad edges, then change them
        1. Find all bad edges
        2. Pick one of those edges randomly
        3. Pick a new random color class
    """

    badvertices = set()
    colors = solution.getvaluedict()
    for _, vertices in colors.items():
        for vertex in vertices:
            if set(solution.getneighbors(vertex)).intersection(vertices):
                badvertices.add(vertex)
                break

    if badvertices:
        badvertex = np.random.choice(list(badvertices))
        pickedcolor = np.random.choice(list(set(colors.keys()) - {solution.getvalue(badvertex)}))
        solution.setvalue(badvertex, pickedcolor)
    return solution

@createnew
def swapvalue(solution):
    """
        Two solutions will be neighbors if one can be transformed
        to the other by moving a vertex from one color class to another.

        To generate a random neighbor, we will randomly pick a
        (nonempty) color class C_OLD' a vertex V in C_OLD'
        and then an integer i, 1 <= i <= k + 1,
        where k is the current number of color classes.
        The neighbor is obtained by moving v to color class C;.
        If i = k + 1 this means that v is moved to a new, previously empty class.
        If v is already in class C; we try again
    """

    colorsused = solution.getvaluedict()
    selectedcolor = np.random.choice(list(colorsused.keys()))
    selectedvertex = np.random.choice(list(colorsused[selectedcolor]))

    pickcolor = lambda col: np.random.choice(list(col.union(
        {min([c for c in range(max(col)+2) if c not in col])})))

    setofcolors = set(colorsused.keys())
    newcolor = pickcolor(setofcolors)
    while selectedcolor == newcolor:
        newcolor = pickcolor(setofcolors)

    #print("new color is {}, colors {}".format(newcolor, colorsused.keys()))
    solution.setvalue(selectedvertex, newcolor)
    return solution

def evaluate(solution):
    """ calculates the cost of the coloring """
    cost = 0

    for color, value in solution.getvaluedict().items():
        numvertices = len(value)
        cost -= numvertices**2

        badedges = 0
        for vertex in value:
            for neighbor in solution.getneighbors(vertex):
                if solution.getvalue(neighbor) == color:
                    badedges += 1
        cost += numvertices*badedges
    # not multiplying by two, because we count each edge 2 times
    # this is due to how I set up my graph structure
    # print("cost is ", cost)
    return cost

def numbadedges(solution):
    """ returns the number of bad edges """
    badedges = 0
    for color, value in solution.getvaluedict().items():
        for vertex in value:
            for neighbor in solution.getneighbors(vertex):
                if solution.getvalue(neighbor) == color:
                    badedges += 1
    return badedges

def validcoloring(solution):
    """ returns true if solution is valid, false otherwise"""
    for color, value in solution.getvaluedict().items():
        for vertex in value:
            for neighbor in solution.getneighbors(vertex):
                if solution.getvalue(neighbor) == color:
                    return False
    return True

def dsatur(graphtoinit):
    """
        input: graph g

        Sets the values for graph in the dsat fashion
        colors are represented as integers, indexed from 0

        output: number of colors used
    """
    queue = PriorityQueue()
    usedcolors = 0
    colors = []

    for k, value in graphtoinit.getgraph().items():
        #print(value,k)
        queue.put((-len(value[1]), k))

    while not queue.empty():
        _, vertex = queue.get()
        ncolors = set()
        for neighbor in graphtoinit.getneighbors(vertex):
            ncolors.add(graphtoinit.getvalue(neighbor))

        for i in colors:
            if i not in ncolors:
                graphtoinit.setvalue(vertex, i)
                break

        if graphtoinit.getvalue(vertex) is None:
            colors.append(usedcolors)
            graphtoinit.setvalue(vertex, usedcolors)
            usedcolors += 1

    return usedcolors-1

def badvalidcoloring(graph):
    """
        Really bad coloring
    """
    i = 0
    for vertex, _ in graph.getgraph().items():
        graph.setvalue(vertex, i)
        i += 1

def randomcoloring(graph, colorstouse):
    """ sets values in graph randomly """
    for vertex, _ in graph.getgraph().items():
        graph.setvalue(vertex, np.random.choice(colorstouse))
