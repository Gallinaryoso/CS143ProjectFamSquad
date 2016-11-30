import packet

class router:

  data_message_size = 64 # This is the size of the message packet

  def __init__(self, id):
    self.id = id
    self.table = {}

  def updateStatic(self, globalTable):
    for host in globalTable.keys():
      subTable = globalTable[host]
      if(self in subTable.keys()):
        self.table[host] = subTable[self]
        
  def updateTable(self, packet):
    host = packet.source

    # If the host is already in the table, compare the weight in the table
    # to the weight seen in this packet. If the new weight is less, replace
    # the data.
    if(host in self.table.keys()):
      data = self.table[host]
      if(data[0] < packet.current_weight):
        self.table[host] = [packet.current_weight, \
          packet.route[len(packet.route) - 2]]

    # If the host is not already in the table, add this data to the table.
    else:
      self.table[host] = [packet.current_weight, \
        packet.route[len(packet.route) - 2]]

  #Initialize new packet with this router as the destination
  def initializeRouterMessages(self, flows):

    # For every flow that exists, make a new packet with the flow src as the
    # source for the packet and this router instance as the destination.
    # This message is then added to the flows list of packets.
    for i in range(len(flows)):
      message = packet(i, flows[i].src, self, 'message', data_message_size, \
        flows[i].src)
      message.route.append(flows[i].src.id)
      flow.packets.append(message) 

  def chooseNextDest(self, newPacket):
    dest = newPacket.destination

    # Get the data corresponding to this destination and choose the next router
    # from the data
    vals = self.table[dest]
    nextRouter = vals[1]

    return nextRouter
    


    

    

    
    
