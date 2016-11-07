
class packet:
  
  def __init__(self, src, dest, payload=None, ack=0):
    self.source = src
    self.destination = dest
    self.payload = payload
    self.acknowledgement = ack
   

