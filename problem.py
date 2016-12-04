#from math
from pulp import *
import numpy as np
import re
from airplane import *

class Problem:
  def __init__(self, landings, planes, takeoffs, first = ""):
    """ Function to initialize the class. This function is run as soon as the class is created. The variable self is the internal name of the object
    This init function also runs all class functions"""
    self.landings = landings               # dict{aircraft type : number of landings}
    self.takeoffs = takeoffs               # dict{aircraft type : number of takeoffs}
    self.planes = planes                   # dict{aircraft type : airplane}
    self.result = {}                       # dict with the results of the solver
    self.first = self.firstplane(first)    # first plane of the batch
    self.last = ""                         # last plane of the schedule
    
    ###PROBLEM DEFINITION
    self.events = self.genevents()         # list of all possible events (see genevents())    
    self.problem = LpProblem("Runway Optimization", LpMinimize)        #Minimizing Problem
    self.variables = LpVariable.dicts("Var", self.events, cat='Integer', lowBound = 0)

    ###OBJECTIVE FUNCTION
    self.costs = self.gencosts()           # dict{event : cost} containing runway time for a certain event
    self.problem += lpSum([self.costs[i]*self.variables[i] for i in self.events]), "Total runway time used"
    
    ###CONSTRAINTS
    self.genconstraints()
    
    ###OUTPUT
    self.genoutput()


  def genconstraints(self):
    """Function to generate the constraints, a string is added to each one of them to describe the constraint textually"""
    if self.first:
      self.problem += self.variables["0->"+self.first] == 1
    for typ in self.landings:
      self.problem += lpSum(self.end_begin(-1, typ)) == self.landings[typ], "Number of " + typ + " landed"
      # For every landing aircraft type there should be a switch to that type (eg. medium -> heavy)
      self.problem += lpSum([self.variables[event] for event in self.events if event.split("->")[-1] == typ and event.split("->")[0] != typ ])>= 1, "switch to " + typ 
      # For every switch to a type there should be a switch away from that type
      self.problem += lpSum(self.end_begin(-1, typ)) - lpSum(self.end_begin(0, typ)) == 0, "head-tails constraint of " + typ    
    for to in self.takeoffs:
      self.problem += lpSum(self.middle(to)) == self.takeoffs[to], "Number of take-offs of " + to
      # For every takeoff aircraft type there should be a switch to that type (eg. medium -> heavy)
      self.problem += lpSum([self.variables[event] for event in self.events if event.split("->")[-1] == "T_"+to and event.split("->")[0] != "T_" + to ])>= 1, "switch to " + "T_" + to 
      # For every switch to a type there should be a switch away from that type
      self.problem += lpSum(self.end_begin(-1, "T_"+to)) - lpSum(self.end_begin(0, "T_"+to)) == 0, "head-tails constraint of " + "T_" + to

    self.problem += lpSum([self.variables[event] for event in self.events if event.split("->")[0] =="0"]) == 1, "starting plane criterion"       #only one starting plane
    self.problem += lpSum([self.variables[event] for event in self.events if event.split("->")[-1] =="0"]) == 1, "last plane criterion"          #only one last plane (this is not counted towards the number of a/c)
  

  def end_begin(self, x, typ):
    """ List comprehension that is quite often used returning a list with only the events beginning or ending with a certain typ from the entire list"""
    return [self.variables[event] for event in self.events if event.split("->")[x] == typ]


  def middle(self, to):
    """ List comprehension filtering the takeoff events from the events"""
    return [(event.split("->")[1:]).count("T_"+to) * self.variables[event] for event in self.events]


  def gencosts(self):
    """ Function to generate a dictionary of costs, which are used in the cost function.
        The costs represent the time a runway is used for a certain event
        This time is dependent on the seperation based on the aircraft class and the approach speed of the aircraft. """
    with open("data/cost.txt", "w") as f:
      f.write("event" + "            " + "cost" + "\n")
      costs = {}
      classes = ['VH', 'H', 'M']
      sep=  [[4,6,7],[3,4,5],[3,3,3]]                       #seperation vh, H , M * vh, H , M
      o_l = {"M":55,"H":60,"VH":65}
      o_t = [[120, 180, 180],[90, 90, 120],[60, 60, 60]]
      path = 8                                              #approach path length in nm
      for event in self.events:
        #try:
        lead = event.split("->")[0]
        follower = event.split("->")[-1]
        if "T" in follower and not "T" in lead:
          cost = o_l[self.planes[lead].wclass()]
        if "T" in lead and "0" in follower:
          cost = 60
        elif (lead == '0' or follower == '0'):
          cost = 0
        elif "T" in follower and "T" in lead:
          i = classes.index(self.planes[lead.split("_")[-1]].wclass())
          j = classes.index(self.planes[follower.split("_")[-1]].wclass())
          cost = o_t[i][j]
        elif "T" not in follower and len(event.split("->")) ==2:
          i = classes.index(self.planes[lead].wclass())
          j = classes.index(self.planes[follower].wclass())
          cost = max([int(((path + sep[i][j])/self.planes[follower].approachspeed - path / self.planes[lead].approachspeed) * 3600)
            , o_l[self.planes[lead].wclass()]])
        elif len(event.split("->"))==3:
          i = classes.index(self.planes[lead].wclass())
          j = classes.index(self.planes[follower].wclass())
          cost = max([int(((path + sep[i][j])/self.planes[follower].approachspeed - path / self.planes[lead].approachspeed) * 3600)
            , sum([ o_l[self.planes[lead].wclass()], 60]) ])
        elif len(event.split("->")) == 4:
          i = classes.index(self.planes[lead].wclass())
          j = classes.index(self.planes[follower].wclass())
          k = classes.index(self.planes[event.split("->")[1].split("_")[-1]].wclass())
          l = classes.index(self.planes[event.split("->")[2].split("_")[-1]].wclass())
          cost = max([int(((path + sep[i][j])/self.planes[follower].approachspeed - path / self.planes[lead].approachspeed) * 3600)
            , sum([ o_l[self.planes[lead].wclass()], o_t[k][l], 60 ])  ])
        costs[event] = cost
        f.write('{:30}'.format(event) + str(cost) + "\n")
    return costs


  def genevents(self):
    """ Function to generate all possible events based on the list of aircraft types present. Events are depicted as the former aircraft type followed by the current aircraft type.
    Everything is listed as a string. A 0 means either the start or the end of the problem (see constraints)"""
    events = []
    for typ in self.landings:
      events.append("0->"+typ)
      events.append(typ+"->0")
      for ty in self.landings:
        events.append(ty + "->" + typ)
        for to in self.takeoffs:
          events.append(ty + "->T_" + to + "->" + typ)
          for to2 in self.takeoffs:            
            events.append(ty + "->T_" + to + "->T_" + to2 + "->" + typ)
      for to in self.takeoffs:
        events.append(typ + "->T_" + to)
    for to in self.takeoffs:
      events.append("T_" + to + "->0")
      for to2 in self.takeoffs:
        events.append("T_" + to + "->T_" + to2)        
    with open("data/events.txt", "w") as f:
      for event in events:
        f.write(event + "\n")
    return events


  def genoutput(self):
    """ Function that writes the problem to an LP file. Following this the problem is solved and the results are printed"""
    # Might be nice to make a more elegant algorithm
    self.problem.writeLP("data/problem.lp")
    with open('data/problemout.txt', 'w') as problemout:
      self.problem.solve()
      print ("status: ", LpStatus[self.problem.status])
      for v in self.problem.variables():
        if not v.varValue == 0.0:
          print(v, "=", v.varValue)
          self.result[v.name] = v.varValue
          problemout.write(v.name + " = " + str(v.varValue) + "\n")
          if v.name.split("__")[-1] == "0":
            self.last = self.getevent(v.name)[0][0]
      print(value(self.problem.objective))         
    self.value = value(self.problem.objective)
    print ("done")


  def getevent(self, var):
    """Takes a problem variable and returns the corresponding event string, as well as a list of discrete events."""
    v = var.split("__")
    v[0] = v[0].split("_")[-1]
    event = ""
    for x in v:
      event += x + "->"
    event = event[:-2]
    return v, event


  def firstplane(self, first):
    if (first and not "T_" in first):
      if first in self.landings:
        self.landings[first] += 1
      else:
        self.landings[first] = 1
        self.planes[first] = airplane(first)
    return first


if __name__ == "__main__":
  # a testcase thats only run if this file is run as main (eg. in terminal: python3 problem.py)
  landings = {"B77W" :2,         
          "A310": 1}
  takeoffs =  {"A310":1}
  planes = {"B77W" : airplane("B77W"),
          "B752" : airplane("B752"),
          "A310": airplane("A310")}
  s = Problem(landings, planes, takeoffs, "A310")