#from math
from pulp import *
import numpy as np
import problem as pr
import re
import airplane as ac
from datetime import datetime
FMT = '%H:%M'

class main:
  """def main():
  lees data + opdelen in blokjes

  loop.....
  koppelen -> gewichtsklasse etc.
  probleem opstellen -> solve
  evaluate performance, last plane etc.
  write
  .....loop
"""
  def __init__(self):
    self.data = []
    self.read_data()
    for landing in self.data[2]:
      print(landing)
    self.generateproblem(self.data[2])


  def classify(self, flights):
    """Classify the aircraft type to certain weight class etc. The function returns two dicts, one containing the types and corresponding number of planes, 
    the other contains the parameters of the type"""
    types = {}
    for flight in flights:
      typ = flight[2]
      try:
        types[typ] += 1
      except: 
        types[typ] = 1
    return types


  def generateproblem(self, flights):
    """Generate a problem using the problem class described in problem.py. """
    types = self.classify(flights)
    planes = {}
    for typ in types:
      a = ac.airplane(typ)
      if a.valid:
        planes[typ] = ac.airplane(typ)
    p = pr.Problem(types, planes)


  def evaluate_performance(self):
    """evaluate the performance compared to the given data"""
    pass

  def read_data(self):
    """Read and chop data into list of strings containing 15min airport time"""
    x = ""
    flights = []
    t0 = ""
    with open("data/log.txt", "w") as fw:
      with open("data/someflights.txt", 'r') as f:
        for lines in f:
            x += lines.strip() + " "
            if re.search("Landed", x):
              try:
                flt = re.findall(r'\s([A-Z0-9]{3,6})\s', x)[0]
                typ = re.findall(r'\s([A-Z]\d+\w*)', x)[0]
                t = re.findall(r'(\d+:\d\d)', x)[0]
                if not t0:
                  t0 = t
                flights.append(["landing", t, typ, flt])              #maybe "landing" not needed -> two different lists? 
                x = ""
              except:
                fw.write("ERROR:     "+ x+ "\n")
                x = ""
              dt = ((datetime.strptime(t, FMT) - datetime.strptime(t0, FMT)).total_seconds())/60
              if dt >= 30 or dt <= -60:
                self.data.append(flights)
                flights = []
                t0 = t
                fw.write(t+ "\n")





    pass

  def write_results(self):
    """Write the results of the problem to new txt file"""
    pass



if __name__ == "__main__":
  m = main()
