import requests
import re

class airplane(object):
  def __init__(self, actype):
    self.actype = actype              #string
    self.valid = True
    self.param()

  def wclass(self):
    ### Weight classes based on faa classification
    try:
      if self.MTOW < 5670:
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
    try:
      r = requests.get("http://www.skybrary.aero/index.php/"+self.actype)
      self.approachspeed, self.MTOW = re.findall(r'V.+?app.+?\s.+?(\d{3})[\w\W]+?MTOW[\w\W]+?(\d{5,6})',r.text)[0]
      with open("data/types.txt", "a") as f:
        f.write(self.actype + "    " + self.approachspeed + "    " + self.MTOW + "\n")
    except:
      self.valid = False
      with open("data/types.txt", "a") as f:
        f.write(self.actype + "\n")

  def param(self):
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
  a = airplane("A388")
  print(a.approachspeed)