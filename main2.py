#from math
from pulp import *
import numpy as np

class Problem:
  def __init__(s):
    s.number = {"heavy" : 3,
              "medium": 3,
              "T": 6}
    s.types = ["heavy", "medium", "T"]
    s.events = s.genevents()
  #  print(events)


    s.costs = {"heavy->medium": 120,
             "medium->heavy": 90, 
             "heavy->heavy": 100, 
             "medium->medium": 100,
             "0->medium": 0,
             "0->heavy": 0}


    print(s.costs["heavy->medium"])
    s.problem = LpProblem("Runway Optimization", LpMinimize)        #Minimizing Problem
    s.variables = LpVariable.dicts("Variables", events, cat='Integer', lowBound = 0)
    s.problem += lpSum([costs[i]*variables[i] for i in events]), "Total runway time used"
    for typ in s.types:
      s.problem += lpSum(s.end_begin(-1)) == s.number[typ], "Number of " + typ + " landed"
      s.problem += lpSum(s.end_begin(-1)) - lpSum(s.end_begin(0)) == 0, "head-tails constraint of " + typ

  #  problem += lpSum([variables["medium->heavy"], variables["heavy->heavy"], variables["heavy"]]) == heavys, "Number of heavys landed"
  #
  #  problem += lpSum([variables["medium->heavy"], variables["heavy"]]) - lpSum([variables["heavy->medium"]]) == 0, "heavys landing criterion"
  #  problem += lpSum([variables["heavy"], variables["medium"]]) == 1
  #  problem += lpSum([variables["medium->heavy"], variables["heavy->medium"]]) >= 1

    s.genoutput()


  def genconstraints(s):
    pass

  def gencosts(s):
    pass
    #s=  [[4,5],[3,3]] H -> M
    #v = [140, 120] approachspeed kts
    #LTL
    #max([(n+s_ij)/vj, 120])
    #LL
    #max([(n+s_ij)/vj, 60])
    #max([,])


  def genevents(s):
    events = []
    for typ in s.types:
      events.append("0->"+typ)
      for ty in types:
        events.append(ty + "->" + typ)
    return events

  def genoutput(s):
    s.problem.writeLP("Simplified_problem.lp")
    with open('problemout.txt', 'w') as problemout:
      s.problem.solve()
      print ("status: ", LpStatus[problem.status])
      problemout.write(str(variables))
      for v in s.problem.variables():
        print(v.name, "=", v.varValue)
    #    problemout.write(str(v.name, "=", v.varValue))
    print ("done")

  def end_begin(s, x):
    return [variables[event] for i, event in enumerate(events) if events[i].split("->")[x] == typ]

if __name__ == "__main__":
  s = Problem()
