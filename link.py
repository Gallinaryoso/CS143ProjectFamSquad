import router.py

class link:
  
  def __init__(self, id, end1, end2, rate, delay, buffer):
    self.id = id
    self.end1 = end1
    self.end2 = end2
    self.rate = rate
    self.delay = delay
    self.buffer = buffer
  
