import router.py

class link:
  
  def __init__(self, id, src, dest, rate, delay, buffer):
    self.id = id
    self.src = src
    self.dest = dest
    self.rate = rate
    self.delay = delay
    self.buffer = buffer
  
