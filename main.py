#from math
from pulp import *
import numpy as np
import problem as pr
import re
import airplane as ac
from datetime import datetime
FMT = '%H:%M'
import matplotlib.pyplot as plt


class main:
  """def main():
  lees data + opdelen in blokjes        DONE

  loop.....
  koppelen -> gewichtsklasse etc.       DONE
  probleem opstellen -> solve           DONE
  evaluate performance, last plane etc.
  write
  .....loop
"""
  def __init__(self):
    self.data = self.read_data("data/DXB_Arrivals_6to6_01-12-16.txt")
    self.data += self.read_data("data/DXB_Departures_6to6_01-12-16.txt")
    self.blocks = self.timify(self.data)
    #print(self.blocks["03:15"])
    self.movements = {}
    self.timesaved = {}
    #self.generateproblem(self.blocks["03:15"], "A388")
    self.runblocks()
    self.evaluate_performance()

  def runblocks(self):
    t = []
    savedtime = []
    first = ""
    for time, flights in sorted(self.blocks.items()):
      p = self.generateproblem(flights, first)
      t.append(time)
      savedtime.append(int(15*60-p.value)/60)
      first = p.last
      #print(time)
    #print(savedtime)
    plt.bar(range(len(t)), savedtime, align='center')
    plt.xticks(range(len(t)), t, rotation='vertical')
    plt.show()

  def timify(self, data):
    """Break up the flights to blocks of 15 minutes"""
    blocks = {}
    for d in data:
      if self.round(d[1]) in blocks:
        blocks[self.round(d[1])].append(d)
      else:
        blocks[self.round(d[1])] = [d]
    return blocks

  def classify(self, block):
    """Classify the aircraft type to certain weight class etc. The function returns two dicts, one containing the types and corresponding number of planes, 
    the other contains the parameters of the type"""
    landings = {}
    takeoffs = {}
    for flight in block:
      typ = flight[2]
      if flight[0] == "Landed":
        try:
          landings[typ] += 1
        except:
          landings[typ] = 1
      if flight[0] == "Departed":
        try:
          takeoffs[typ] += 1
        except:
          takeoffs[typ] = 1
    return landings, takeoffs

  def generateproblem(self, block, first = ""):
    """Generate a problem using the problem class described in problem.py. """
    landings, takeoffs = self.classify(block)
    planes = {}
    for typ in landings:
      a = ac.airplane(typ)
      planes[typ] = ac.airplane(typ)
    for typ in takeoffs:
      a = ac.airplane(typ)
      planes[typ] = ac.airplane(typ)
    p = pr.Problem(landings, planes, takeoffs, first)
    return p




  def evaluate_performance(self):
    """evaluate the performance compared to the given data"""
    x, y = [], []
    for key, value in sorted(self.blocks.items()):
      x.append(key)
      y.append(len(value))
    print (len(x))
    plt.bar(range(len(x)), y, align='center')
    plt.xticks(range(len(x)), x, rotation='vertical')
    plt.show()

  def read_data(self, file):
    """Read and chop data into list of strings containing 15min airport time"""
    x = ""
    flights = []
    data = []
    t0 = ""
    with open("data/log.txt", "w") as fw:
      with open(file, 'r') as f:
        for lines in f:
            x += lines.strip() + " "
            action = re.search(r'(Landed|Departed)', x)            
            if action:
              try:
                t, flt, typ = self.extractflight(x)
                x = ""
                data.append([action.group(0), t, typ, flt])
                fw.write(t + "\n")              
              except:
                fw.write("ERROR:     "+ x+ "\n")
                x = ""
    return data

  def extractflight(self, x):
    flt = re.findall(r'\s([A-Z0-9]{3,6})\s', x)[0]
    typ = re.findall(r'[\w\)]{3,}\s+?([A-Z]\d+\w*)', x)[0]
    t = re.findall(r'(\d+):(\d\d)\s(PM|AM)', x)[0]
    #print(t)
    if t[-1] == "PM":
      t = str(int(t[0])+ 12) + ":" + str(t[1])
    else: t = str(t[0]) + ":" + str( t[1])
    return t, flt, typ


  def write_results(self, block):
    """Write the results of the problem to new txt file"""
    pass

    

  def round(self, t, to = 15):
    mi = int(t.split(":")[-1])
    minutes = [15,30,45,60]#list(range(0,60,to))
    for x in minutes:
      if mi < x:
        return t.split(":")[0].zfill(2) + ":" + str(x-to).zfill(2)


if __name__ == "__main__":
  m = main()
