import requests
import re

class airplane(object):
  """Object containing the approach speed, weightclass and MTOW of a certain aircraft type
  It is initialized with an aircraft type only. The rest is found in a data file or online"""
  def __init__(self, actype):
    self.actype = actype              # string
    self.approachspeed = 120          # kts, default value, only used if aircraft type not found
    self.valid = True
    self.param()

  def wclass(self):
    ### Returns weight classes based on icao classification
    if self.actype == "A388":
      return "VH"
    elif self.wtc:
      return self.wtc
    elif self.MTOW == 0:
      return "M"

  def search(self):
    """Function that looks on the site skybrary.aero for the airplane type. If it's found the 
    approachspeed and MTOW are extracted and saved to the types.txt file for speed on subsequent runs."""
    try:
      r = requests.get("http://www.skybrary.aero/index.php/"+self.actype)
    except:
      pass
    try:
      self.wtc = re.findall(r'WTC.+\s.+?([A-Z]{1,2})', r.text)[0]
    except:
      self.wtc = "M"
    try:  
      self.approachspeed = re.findall(r'V.+?app.+\s.+?(\d{3})', r.text)[0]
    except:
      app = {"M" : 120, "H" : 140, "VH" : 160}
      self.approachspeed = app[self.wtc]
    try:
     self.MTOW = re.findall(r'MTOW[\w\W]+?(\d{4,6})',r.text)[0]
    except:
      self.MTOW = 0
    with open("data/types.txt", "a") as f:
      f.write(self.actype + "    " + str(self.approachspeed) + "    " + str(self.MTOW) + "    " + self.wtc + "\n")

  def param(self):
    """Function that runs through the types.txt file and checks for the aircraft type. If it isn't in the file
    an internet search is tried."""    
    x = 0
    try:
      with open("data/types.txt", "r") as f:
        for line in f:
          if self.actype in line:
            try:
              r = re.findall(r'\s(\d+)\s+?(\d+)\s+?([A-Z]{1,2})',line)[0]
              self.MTOW = int(r[1])
              self.approachspeed = int(r[0])
              self.wtc = r[2]
              x = 1              
            except:
              x = 1
              pass
    except:
      pass
    if not x:
      self.search()

if __name__ == "__main__":
  a = airplane("B77W")
  print(a.approachspeed)