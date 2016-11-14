
class packet:
  
  def __init__(self, id, src, dest, size):
    self.id = id
    self.source = src
    self.destination = dest
    self.size = size #bytes
    self.delay = 0
