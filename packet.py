
class packet:
  
  def __init__(self, src, dest, size, ack=false):
    self.source = src
    self.destination = dest
    self.size = size
    self.acknowledgement = ack
