
class packet:
  
  def __init__(self, src, dest, size):
    self.source = src
    self.destination = dest
    self.size = size #bytes
    self.delay = 0
