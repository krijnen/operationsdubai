#from math
from pulp import *
import numpy as np
import problem as pr
import re
import airplane as ac
#from datetime import datetime
#FMT = '%H:%M'
import matplotlib.pyplot as plt


class main:
  """
  Main class of the Dubai runway problem algorithm (though it could be used for any runway). It takes flight data from a text file from 24flightradar.
  The flights are processed per block of fifteen minutes. Each block is analyzed as a seperate linear problem.
  The blocks are connected through an extra constraint regarding the last plane of 
  the first block and first plane of the following block. The linear problems are then solved and the results are analyzed.
  For more information on the problem formulation, check the file problem.py and data/problem.lp for the complete formulation 
  of the problem. Lots of underlying variables and data are written to te
  More information on the assumptions are formulated in a report.
  @authors: Hielke Krijnen, Bram Doedijns, Regis van Som
"""
  def __init__(self):
    ### Read data
    self.data = self.read_data("data/DXB_Arrivals_6to6_01-12-16.txt")
    self.data += self.read_data("data/DXB_Departures_6to6_01-12-16.txt")

    ### Cut into blocks of 15 minutes
    self.blocks = self.timify(self.data)
    self.movements = {}
    self.timesaved = {}

    ### Create a problem from every block and evaluate its performance
    self.runblocks()
    self.evaluate_performance()

  def runblocks(self):
    """Takes the blocks dictionary and runs through each block
    Based on the data of the block, a problem is created and solved.
    The last plane of the solution is recorded and used for the next problem"""
    t = []
    savedtime = []
    first = ""
    for time, flights in sorted(self.blocks.items()):
      p = self.generateproblem(flights, first)
      t.append(time)
      savedtime.append(int(15*60-p.value)/60)      
      first = p.last
    ### TODO WRITE TO RESULTS
    print(max(savedtime))
    print(min(savedtime))
    print(sum(savedtime))
    print(sum(savedtime)/len(savedtime))
    plt.bar(range(len(t)), savedtime, align='center')
    savedtime = [int(sum(savedtime[i:i+3])/4) for i in range(0, len(savedtime), 4)]
    t = [x for x in t if t.index(x) % 4 == 0]
    plt.bar(range(0,len(t)*4, 4), savedtime, align='center', color = "red")
    plt.xticks(range(0,len(t)*4, 4), t, rotation='vertical')
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
    """Sort the aircraft type to certain events. The function returns two dicts, containing the types and corresponding number of movements."""
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
    x = [i for i in x if x.index(i) % 4 == 0]
    plt.xticks(range(0,len(x)*4,4), x, rotation='vertical')
    plt.show()

  def read_data(self, file):
    """Read data into list of strings"""
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
    """Extracts type of the aircraft, the type and the scheduled time of the 
    flight from the list"""    
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
    """Round a time string "HH:MM" to a certain number of minutes (rounded down) """
    mi = int(t.split(":")[-1])
    #minutes = [15,30,45,60]#list(range(0,60,to))
    for x in range(0,61,to):
      if mi < x:
        return t.split(":")[0].zfill(2) + ":" + str(x-to).zfill(2)
    


if __name__ == "__main__":
  m = main()