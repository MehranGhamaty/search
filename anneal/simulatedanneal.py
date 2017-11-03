#/bin/python3.6

"""
    provides a simulated annealing function
"""


import numpy as np
import stochastictunnel as st
#from scipy import constants


def simulatedannealing(solution, #pylint: disable-msg=too-many-arguments,too-many-locals,too-many-branches,line-too-long
                       initprob, temperatureupdate,
                       freezelimit, sizefactor, cutoff,
                       upperbound, minpercent,
                       objectivefunc, perturbator,
                       tunnel=False,
                       gamma=None,
                       ploton=False):
    """
        This can heavily be improved by saving the delta
        and applying it to the solution instead of remaking a new object every time
    """
    if tunnel:
        originalobjectivefunction = objectivefunc

    num = upperbound(solution)
    minimum = (solution, objectivefunc(solution))
    history = [(0, minimum[1])]
    print("starting as {}".format(minimum))
    temperature = initprob*sizefactor

    freezecount = 0
    while freezecount < freezelimit:
        trials = 0
        changes = 0
        changed = False
        #print("changes ", changes)
        #print("temperature {}".format(temperature))
        while trials < sizefactor*num and changes < cutoff*num:
            #print("trial", trials)
            trials += 1


            newsolution = perturbator(solution)
            newscore = objectivefunc(newsolution)
            delta = newscore - objectivefunc(solution)
            if newsolution != solution: #so fixed_k will actually stop
                if delta <= 0:
                    changes += 1
                    changed = True
                    solution = newsolution
                    if getattr(perturbator, 'accept', None):
                        perturbator.accept()
                    if callable(ploton):
                        ploton(newsolution)
                elif delta > 0 and np.exp(-delta/temperature) >= np.random.random():
                    solution = newsolution
                    changes += 1
                    if hasattr(objectivefunc, 'accept'):
                        objectivefunc.accept()
                    if callable(ploton):
                        ploton(newsolution)

                if newscore < minimum[1]:
                    minimum = (newsolution, newscore)

            history.append((history[-1][0]+1, minimum[1]))


        temperature = temperatureupdate(temperature)
        if changed:
            freezecount = 0
        elif changes/trials < minpercent:
            freezecount += 1
            if tunnel:
                print("tunneling!!!!!!!!!!!!!")
                if callable(gamma):
                    tmpgamma = gamma(objectivefunc(solution), minimum[1])
                else:
                    tmpgamma = gamma
                objectivefunc = st.stochastictunnel(originalobjectivefunction, minimum[1], tmpgamma)
        print("freezecount", freezecount)

    print("ending as {}".format(minimum))
    return minimum, history
