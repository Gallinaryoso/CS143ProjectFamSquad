import router.py

class link:
  
  def __init__(self, id, end_1, end_2, capacity, rate, delay, buffer):
    self.id = id
    self.end_1 = end_1
    self.end_2 = end_2
    self.capacity = capacity #in Mbps
    self.rate = rate # in Mbps 
    self.delay = delay # in ms 
    self.buffer = buffer # in KB 
  
