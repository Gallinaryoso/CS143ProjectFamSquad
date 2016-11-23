
class flow:
  
  def __init__(self, src, dest, dataAMT, start):
    self.src = src # source host of flow
    self.dest = dest #destination host of flow
    self.amt = dataAMT # MB
    self.start = start # seconds
    self.packets = [] # list of all packets needed in flow
