
class packet:
  
  def __init__(self, src, dest, ack=false):
    self.source = src
    self.destination = dest
    self.acknowledgement = ack
