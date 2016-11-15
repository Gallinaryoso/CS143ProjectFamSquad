
class packet:
  
  def __init__(self, id, src, dest, size):
    self.id = id
    self.source = src
    self.destination = dest
    self.size = size #bytes
    self.delay = 0
    self.route = []
    self.router = 0
    self.time_left_host = -1
    self.dropped = False 
