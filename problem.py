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
    #self.schedule = self.rearrangeoutput()
    #self.schedule = self.filteroutput()

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
    self.problem += lpSum([self.variables[event] for event in self.events if event.split("->")[0] =="0"]) == 1, "starting plane criterion"       #only one starting plane
    self.problem += lpSum([self.variables[event] for event in self.events if event.split("->")[-1] =="0"]) == 1, "last plane criterion"          #only one last plane (this is not counted towards the number of a/c)


 
  def gencosts(self):
    """ Function to generate a dictionary of costs, which are used in the cost function.
        The costs represent the time a runway is used for a certain event
        This time is dependent on the seperation based on the aircraft class and the approach speed of the aircraft. """
    with open("data/cost.txt", "w") as f:
      f.write("event" + "            " + "cost" + "\n")
      costs = {}
      classes = ['vheavy', 'heavy', 'medium']
      sep=  [[4,6,7],[3,4,5],[3,3,3]]                       #seperation vh, H , M * vh, H , M
      path = 8                                              #approach path length in nm
      for event in self.events:
        try:
          lead = event.split("->")[0]
          follower = event.split("->")[-1]
          if "T" in follower:
            cost = 65
          elif (lead == '0' or follower == '0'):
            cost = 0
          else:
            i = classes.index(self.planes[lead].wclass())
            j = classes.index(self.planes[follower].wclass())
            cost = max([int(((path + sep[i][j])/self.planes[follower].approachspeed - path / self.planes[lead].approachspeed) * 3600),(len(event.split("->"))-1)*65]) 
        except:
          print ("cost of " + lead + " " + follower + " not found")
          cost = 1000
        costs[event] = cost
        f.write('{:30}'.format(event) + str(cost) + "\n")            ####FORMAT
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

  def end_begin(self, x, typ):
    """ List comprehension that is quite often used returning a list with only the events beginning or ending with a certain typ from the entire list"""
    return [self.variables[event] for event in self.events if event.split("->")[x] == typ]

  def middle(self, to):
    """ List comprehension filtering the takeoff events from the events"""
    return [(event.split("->")[1:]).count("T_"+to) * self.variables[event] for event in self.events]

  def rearrangeoutput(self):
    """Function to rearrange the result into a schedule."""
    ###TODO: explore option tree (at this points it takes the first option only, not always leading to the correct soln)
    result = self.result
    schedule = []
    last = "0"
    for i in range(1,1000):
      for r in result:
        if r.split("_")[1] == last and r.split("_")[-1]!="0":
          schedule.append(r)
          result[r] -= 1
          if result [r] == 0:
            del result[r]
          for t in result:
            if t.split("_")[-1] == r:
              while True:
                schedule.append(t)
                result[t] -= 1
                if result [t] <= 0:
                  del result[t]
                  break
          last = r.split("_")[-1]
          break
      if len(result) == 1:
        for r in result:
          schedule.append(r)
    with open("data/problemout.txt", "a") as f:
      for s in schedule:
        f.write(s+"\n")
    return schedule

  def filteroutput(self):
    """Function that takes the rearranged output and filters it to a list of single events"""
    schedule = []
    for event in self.schedule:
      for i, flight in enumerate(self.getevent(event)[0]):
        if i != 0:
          if flight != "0":
            schedule.append(flight)
    with open("data/problemout.txt", "a") as f:
      for s in schedule:
        f.write(s+"\n")
    return schedule

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
    ###TODO takeoffs
    if first:
      if first in landings:
        self.landings[first] += 1
      else:
        self.landings[first] = 1
        planes[first] = airplane.airplane(first)
    return first


if __name__ == "__main__":
  # a testcase thats only run if this file is run as main (eg. in terminal: python3 problem.py)
  landings = {"B77W" :2,
          "B752" : 3,
          "A310": 3}
  takeoffs =  {"B77W" :2,
          "B752" : 3,
          "A310": 3}
  planes = {"B77W" : airplane("B77W"),
          "B752" : airplane("B752"),
          "A310": airplane("A310")}
  s = Problem(landings, planes, takeoffs, "A310")