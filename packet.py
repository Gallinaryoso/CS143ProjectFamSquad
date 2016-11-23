
class packet:
  
  def __init__(self, id, src, dest, type, size, current_router, next_router):
    self.id = id #ID of packet
    self.source = src #source of packet
    self.destination = dest #destination of packet
    self.type = type #type as packet, ack, or route
    self.size = size #packet size in bytes
    self.current_router = current_router #current router of packet
    self.next_router = next_router #next router for packet to go to
    self.delay = 0 #delay due to congestion from a particular link
    self.route = [] #route that a packet has traveled already
    self.route_index = 0 #index of route array where packet/ack is
    #self.arrived_at_dest = -1
