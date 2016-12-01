class packet:
  
  def __init__(self, id, src, dest, type, size, current_router):
    self.id = id #ID of packet
    self.source = src #source of packet
    self.destination = dest #destination of packet
    self.type = type #type as packet, ack, or message
    self.size = size #packet size in bytes
    self.current_router = current_router #current router of packet
    self.current_time = -1 #time of a packet, after congestion
    self.route = [] #route that a packet has traveled already
    self.route_index = 0 #index of route array where packet/ack is
    self.start_time = -1 #when the packet started buffering in the flow
    self.current_weight = 0 #keeps track of link weights encountered for message
    self.destDict = {} #keeps track of all the paths to self.src