import router.py

class link:
  
  def __init__(self, id, end_1, end_2, rate, delay, buffer):
    self.id = id
    self.end_1 = end_1
    self.end_2 = end_2
    self.rate = rate
    self.delay = delay
    self.buffer = buffer
  
