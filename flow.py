
class flow:
  
  def __init__(self, src, dest, dataAMT, start):
    self.src = src
    self.dest = dest
    self.amt = dataAMT # MB
    self.start = start # seconds
    self.rate = 0  # Mbps
