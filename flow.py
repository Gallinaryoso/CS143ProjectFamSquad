
class flow:
  
  def __init__(self, src, dest, dataAMT, start):
    self.src = src # source host of flow
    self.dest = dest # destination host of flow
    self.amt = dataAMT # amount of data in MB
    self.start = start # flow start time in seconds
    self.packets = [] # list of all packets needed in flow
    self.current_packet = 1 # index of packet that is next in line
