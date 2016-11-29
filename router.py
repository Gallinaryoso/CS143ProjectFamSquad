import packet

class router:

  # This is defined globally for all instances of the router class
  # This is a dictionary of dictionaries for each host.
  globalTable = {}
  data_message_size = 64

  def __init__(self, id):
    self.id = id
    self.table = {}

  def updateTable(self, globalTable):
    for host in globalTable:
      routers = globalTable[host]
      self.table[host] = routers[self]

  #Initialize new packet with this router as the destination
  def initializeRouterMessages(self, flows):
    packets = []
    # For every host that exists, make a new packet 
    for i in range(len(flows)):
      message = packet(i, flows[i].src, self, 'message', data_message_size, \
        flows[i].src)
      message.route.append(flows[i].src.id)
      packets.append(message)    

  def chooseNextDest(self, newPacket):
    dest = newPacket.destination
    nextRouter = self.table[dest]
    return nextRouter
    


    

    

    
    
