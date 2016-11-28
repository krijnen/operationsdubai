#from math
from pulp import *
import numpy as np

class Problem:
  def __init__(self, types, landings, to_events, takeoffs):
    """ Function to initialize the class. This function is run as soon as the class is created. The variable self is the internal name of the object"""            
    self.landings = landings              # nr of landings
    self.types = types                    # aircraft types
    self.to_events = to_events            # takeoffs
    self.takeoffs = takeoffs
    self.events = self.genevents()
    self.costs = self.gencosts()    
    self.problem = LpProblem("Runway Optimization", LpMinimize)        #Minimizing Problem
    self.variables = LpVariable.dicts("Variables", self.events, cat='Integer', lowBound = 0)
    self.problem += lpSum([self.costs[i]*self.variables[i] for i in self.events]), "Total runway time used"   #objective function
    #self.problem += lpSum([self.costs[i]*self.variables[i] for i in self.ll_events + self.ltl_events + self.lttl_events]), "Total runway time used"  with added Takeoffs
    self.genconstraints()

    self.genoutput()


  def genconstraints(self):
    """Function to generate the constraints, a string is added to each one of them to describe the constraint textually"""
    for typ in self.types:
      self.problem += lpSum(self.end_begin(-1, typ)) == self.landings[typ], "Number of " + typ + " landed"
      # For every landing aircraft type there should be a switch to that type (eg. medium -> heavy)
      self.problem += lpSum([self.variables[event] for event in self.events if event.split("->")[-1] == typ and event.split("->")[0] != typ ])>= 1, "switch to " + typ 
      # For every switch to a type there should be a switch away from that type
      self.problem += lpSum(self.end_begin(-1, typ)) - lpSum(self.end_begin(0, typ)) == 0, "head-tails constraint of " + typ
    for to in self.to_events:
      self.problem += lpSum(self.middle(to)) == self.takeoffs[to], "Number of take-offs of " + to
    self.problem += lpSum([self.variables[event] for event in self.events if event.split("->")[0] =="0"]) == 1, "starting plane criterion"       #only one starting plane
    self.problem += lpSum([self.variables[event] for event in self.events if event.split("->")[-1] =="0"]) == 1, "last plane criterion"          #only one last plane (this is not counted towards the number of a/c)

  #  problem += lpSum([variables["medium->heavy"], variables["heavy"]]) - lpSum([variables["heavy->medium"]]) == 0, "heavys landing criterion"
  #  problem += lpSum([variables["heavy"], variables["medium"]]) == 1
    #self.problem += lpSum([self.variables["medium->heavy"], self.variables["heavy->medium"]]) >= 1

 
  def gencosts(self):
    """ Function to generate a dictionary of costs, which are used in the cost function.
        The costs represent the time a runway is used for a certain event
        This time is dependent on the seperation based on the aircraft class and the approach speed of the aircraft. """
    costs = {}
    sep=  [[4,5,6],[3,4,5],[3,3,4]]   #seperation vh, H , M * vh, H , M
    v = [150, 140, 120]     # approachspeed kts (make dict!)
    if len(v) != len(self.types):
      print("types and approachspeeds dont match!!!")
    for event in self.events:
      try:
        i = self.types.index(event.split("->")[0])
        j = self.types.index(event.split("->")[-1])
        cost = max([int((8 + sep[i][j])/v[j] * 3600),60])
      except:
        cost = 0
      costs[event] = cost
      print (event + "  " + str(cost))
    print ("\n")
    return costs
    #LTL
    #max([(n+s_ij)/vj, 120])
    #LL
    #max([(n+s_ij)/vj, 60])
    #max([,])


  def genevents(self):
    """ Function to generate all possible events based on the list of aircraft types present. Events are depicted as the former aircraft type followed by the current aircraft type.
    Everything is listed as a string. A 0 means either the start or the end of the problem (see constraints)"""
    events = []
    for typ in self.types:
      events.append("0->"+typ)
      events.append(typ+"->0")
      for ty in self.types:
        events.append(ty + "->" + typ)
        for to in self.to_events:
          events.append(ty + "->" + to + "->" + typ)
          for to2 in self.to_events:
            events.append(ty + "->" + to + "->" + to2 + "->" + typ)
    #for event in events:
      #print (event)
    return events

  def genoutput(self):
    """ Function that writes the problem to an LP file. Following this the problem is solved and the results are printed"""
    # Might be nice to make a more elegant algorithm
    self.problem.writeLP("Simplified_problem.lp")
    with open('problemout.txt', 'w') as problemout:
      self.problem.solve()
      print ("status: ", LpStatus[self.problem.status])
      problemout.write(str(self.variables))
      for v in self.problem.variables():
        if not v.varValue == 0.0:
          print(v.name, "=", v.varValue)
      print(value(self.problem.objective))
    #    problemout.write(str(v.name, "=", v.varValue))
    print ("done")

  def end_begin(self, x, typ):
    """ List comprehension that is quite often used returning a list with only the events beginning or ending with a certain typ from the entire list"""
    return [self.variables[event] for event in self.events if event.split("->")[x] == typ]
    #return [self.variables[event] for event in self.events + ltl_events + lttl_events if event.split("->")[x] == typ]

  def middle(self, to):
    return [(event.split("->")).count(to) * self.variables[event] for event in self.events]

if __name__ == "__main__":
  # a simple testcase thats only run if this file is run
  types = ["vheavy", "heavy", "medium"]
  landings = {"vheavy" :2,
          "heavy" : 3,
          "medium": 3}

  takeoffs = {"T_m" : 3,
              "T_h" : 5}

  print (takeoffs["T_m"])
  to_events = ["T_m", "T_h"]

  s = Problem(types, landings, to_events, takeoffs)