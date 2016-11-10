
class packet:
  
  def __init__(self, src, dest, payload=None, ack=false):
    self.source = src
    self.destination = dest
    self.payload = payload
    self.acknowledgement = ack
