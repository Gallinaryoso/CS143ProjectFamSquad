
class packet:
  
  def __init__(self, source, destination, payload=None, acknowledgement=0):
    self.source = source
    self.destination = destination
    self.payload = payload
    self.acknowledgement = acknowledgement
   

