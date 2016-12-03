import requests
import re

class airplane(object):
  """Object containing the approach speed, weightclass and MTOW of a certain aircraft type
  It is initialized with an aircraft type only. The rest is found in a data file or online"""
  def __init__(self, actype):
    self.actype = actype              # string
    self.approachspeed = 140          # kts, default value, only used if aircraft type not found
    self.valid = True
    self.param()

  def wclass(self):
    ### Returns weight classes based on faa classification
    try:
      if self.wtc:
        return self.wtc
      elif self.MTOW < 5670:
        return 'small'
      elif self.MTOW < 18600:
        return 'medium'        
      elif self.MTOW < 115666:
        return 'heavy'
      else:
        return 'vheavy'
    except:
      return 'medium'

  def search(self):
    """Function that looks on the site skybrary.aero for the airplane type. If it's found the 
    approachspeed and MTOW are extracted and saved to the types.txt file for speed on subsequent runs."""
    try:
      r = requests.get("http://www.skybrary.aero/index.php/"+self.actype)
      try:  
        self.approachspeed = re.findall(r'V.+?app.+\s.+?(\d{3})', r.text)[0]
      except:
        self.approachspeed = "140"
      try:  
       self.MTOW = re.findall(r'MTOW[\w\W]+?(\d{4,6})',r.text)[0]
      except:
        self.MTOW = ""
      try:
        self.wtc = re.findall(r'WTC.+\s.+?([A-Z]{1,2})', r.text)[0]
      except:
        self.wtc = self.wclass()
    except:
      pass
    try:
      with open("data/types.txt", "a") as f:
        f.write(self.actype + "    " + self.approachspeed + "    " + self.MTOW + "    " + self.wtc + "\n")
    except:
      self.valid = False      
      with open("data/types.txt", "a") as f:
        f.write(self.actype + "\n")
    ###TODO look up WTClass WTC
    ###Seperate search

  def param(self):
    """Function that runs through the types.txt file and checks for the aircraft type. If it isn't in the file
    an internet search is tried."""    
    x = 0
    try:
      with open("data/types.txt", "r") as f:
        for line in f:
          if self.actype in line:
            try:
              r = re.findall(r'\s(\d+)\s+?(\d+)',line)[0]
              self.MTOW = int(r[1])
              self.approachspeed = int(r[0])
              x = 1
              break
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