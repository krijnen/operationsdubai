#from math
from pulp import *

heavys = 3
mediums = 3

events = ["h->m", "m->h", "h->h", "m->m", "m", "h"]

costs = {"h->m": 120,
         "m->h": 90, 
         "h->h": 100, 
         "m->m": 100,
         "m": 0,
         "h": 0}

problem = LpProblem("Runway Optimization", LpMinimize)
variables = LpVariable.dicts("Variables", events, cat='Integer', lowBound = 0)

problem += lpSum([costs[i]*variables[i] for i in events]), "Total runway time used"
problem += lpSum([variables[events[1]], variables[events[2]]]) == heavys, "Number of heavys landed"
problem += lpSum([variables[events[0]], variables[events[3]]]) == mediums, "Number of mediums landed"
problem += lpSum([variables[events[0]], variables[events[3]]]) - lpSum([variables[events[1]], variables[events[3]]]) == 0, "heavys landing criterion"
problem += lpSum([variables[events[1]], variables[events[2]]]) - lpSum([variables[events[0]], variables[events[2]]]) == 0, "mediums landing criterion" 
problem += lpSum([variables[events[0]], variables[events[1]]]) >= 1


problem.writeLP("Simplified_problem.lp")
with open('problemout.txt', 'w') as problemout:
  problem.solve()
  print ("status: ", LpStatus[problem.status])
  problemout.write(str(variables))
  for v in problem.variables():
    print(v.name, "=", v.varValue)
print ("done")
