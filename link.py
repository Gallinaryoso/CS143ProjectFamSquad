import router.py

class link:
  
  def __init__(self, id, end_1, end_2, rate, delay, buffer_capacity):
    self.id = id
    self.end_1 = end_1
    self.end_2 = end_2
    self.rate = rate # in Mbps
    self.delay = delay # in ms 
    self.buffer_capacity = buffer_capacity # in KB
    self.buffer_occupancy = 0 # in KB
    self.buffer_packets = [] # all the packets in the buffer
