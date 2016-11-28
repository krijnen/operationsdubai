#from math
from pulp import *
import numpy as np

class Problem:
  def __init__(s, types, landings ):
    s.landings = landings             # nr of landings
    s.types = types                   # aircraft types
#    s.to_types = ["T_m", "T_h"]      # takeoffs
    s.events = s.genevents()
    s.costs = s.gencosts()    
    s.problem = LpProblem("Runway Optimization", LpMinimize)        #Minimizing Problem
    s.variables = LpVariable.dicts("Variables", s.events, cat='Integer', lowBound = 0)
    s.problem += lpSum([s.costs[i]*s.variables[i] for i in s.events]), "Total runway time used"   #objective function
    #s.problem += lpSum([s.costs[i]*s.variables[i] for i in s.ll_events + s.ltl_events + s.lttl_events]), "Total runway time used"  with added Takeoffs
    s.genconstraints()

    s.genoutput()


  def genconstraints(s):
    """Function to generate the constraints, a string is added to each one of them to describe the constraint textually"""
    for typ in s.types:
      s.problem += lpSum(s.end_begin(-1, typ)) == s.landings[typ], "Number of " + typ + " landed"
      s.problem += lpSum(s.end_begin(-1, typ)) - lpSum(s.end_begin(0, typ)) == 0, "head-tails constraint of " + typ
      s.problem += lpSum([s.variables[event] for event in s.events if event.split("->")[-1] == typ and event.split("->")[0] != typ ])>= 1, "switch to " + typ
    s.problem += lpSum([s.variables[event] for event in s.events if event.split("->")[0] =="0"]) == 1, "starting plane criterion"       #only one starting plane
    s.problem += lpSum([s.variables[event] for event in s.events if event.split("->")[-1] =="0"]) == 1, "last plane criterion"          #only one last plane
    #  problem += lpSum([variables["medium->heavy"], variables["heavy->heavy"], variables["heavy"]]) == heavys, "Number of heavys landed"
  #
  #  problem += lpSum([variables["medium->heavy"], variables["heavy"]]) - lpSum([variables["heavy->medium"]]) == 0, "heavys landing criterion"
  #  problem += lpSum([variables["heavy"], variables["medium"]]) == 1
    #s.problem += lpSum([s.variables["medium->heavy"], s.variables["heavy->medium"]]) >= 1

 
  def gencosts(s):
    """ Function to generate a dictionary of costs, which are used in the cost function.
        The costs represent the time a runway is used for a certain event
        This time is dependent on the seperation based on the aircraft class and the approach speed of the aircraft. """
    costs = {}
    sep=  [[4,5,6],[3,4,5],[3,3,4]]   #seperation vh, H , M * vh, H , M
    v = [150, 140, 120]     # approachspeed kts (make dict!)
    if len(v) != len(s.types):
      print("types and approachspeeds dont match!!!")
    for event in s.events:
      try:
        i = s.types.index(event.split("->")[0])
        j = s.types.index(event.split("->")[-1])
        cost = max([int((8 + sep[i][j])/v[j] * 3600),60])
      except:
        cost = 0
      costs[event] = cost
    print(costs)
    print (sep[0])
    return costs
    #LTL
    #max([(n+s_ij)/vj, 120])
    #LL
    #max([(n+s_ij)/vj, 60])
    #max([,])


  def genevents(s):
    """ Function to generate all possible events based on the list of aircraft types present. """
    events = []
    for typ in s.types:
      events.append("0->"+typ)
      events.append(typ+"->0")
      for ty in s.types:
        events.append(ty + "->" + typ)
    return events

  def genoutput(s):
    """ Function that writes the problem to an LP file. Following this the problem is solved and the results are printed"""
    # Might be nice to make a more elegant algorithm
    s.problem.writeLP("Simplified_problem.lp")
    with open('problemout.txt', 'w') as problemout:
      s.problem.solve()
      print ("status: ", LpStatus[s.problem.status])
      problemout.write(str(s.variables))
      for v in s.problem.variables():
        if not v.varValue == 0.0:
          print(v.name, "=", v.varValue)
      print(value(s.problem.objective))
    #    problemout.write(str(v.name, "=", v.varValue))
    print ("done")

  def end_begin(s, x, typ):
    """ List comprehension that is quite often used returning a list with only the events beginning or ending with a certain typ from the entire list"""
    return [s.variables[event] for event in s.events if event.split("->")[x] == typ]
    #return [s.variables[event] for event in s.events + ltl_events + lttl_events if event.split("->")[x] == typ]

if __name__ == "__main__":
  types = ["vheavy", "heavy", "medium"]
  landings = {"vheavy" :2,
          "heavy" : 3,
          "medium": 3,
          "T": 6}

  s = Problem(types, landings)
