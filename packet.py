
class packet:
  
  def __init__(self, id, src, dest, type, size, current_router):
    self.id = id
    self.source = src
    self.destination = dest
    self.type = type #packet, ack, or route
    self.size = size #bytes
    self.current_router = current_router
    self.delay = 0
    self.route = []
    self.route_index = 0
    #self.arrived_at_dest = -1
