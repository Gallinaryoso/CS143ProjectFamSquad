from packet import packet
import shortestPath as sP
import sys

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
        
  def updateTable(self, source, sDict):
    for r in sDict.keys():
      if(r == self):
        paths = sDict[r]
        bestPath = paths[0]
        if(len(paths) > 1):
          bestPath = sP.findMinimumPath(paths)

        if(source in self.table.keys()):
          data = self.table[source]
          if(bestPath[1] == data[1]):
            self.table[source][0] = bestPath
          elif(bestPath[0] < data[0]):
            self.table[source] = bestPath
        else:
          self.table[source] = bestPath

  # # This takes in a packet and updates the table according to the data in the
  # # packet. The current router of the packet is the router the packet just
  # # came from (so the next step).
  # def updateTable(self, packet):
  #   # Get the host that this packet was sent from
  #   host = packet.source

  #   # If the host is already in the table, compare the weight in the table
  #   # to the weight seen in this packet. If the new weight is less, replace
  #   # the data.
  #   if(host in self.table.keys()):

  #     # Get the next step and weightdata
  #     data = self.table[host]

  #     # If the next step is the inputted packets current router, update the 
  #     # weight of that next step.
  #     if(data[1] == packet.current_router):
  #       self.table[host][0] = packet.current_weight

  #     # Else, if its a different next step, check if the new weight is less 
  #     # than the old weight. If so, update the weight and next step.
  #     elif(packet.current_weight < data[0]):
  #       # print("Old Table for " + self.id)
  #       # for key in self.table:
  #       #   print("Key: " + key.id)
  #       #   print("Weight: " + str(self.table[key][0]))
  #       #   print("Next Step: " + self.table[key][1].id)

  #       self.table[host] = [packet.current_weight, packet.current_router]

  #       # print("New Table for " + self.id)
  #       # for key in self.table:
  #       #   print("Key: " + key.id)
  #       #   print("Weight: " + str(self.table[key][0]))
  #       #   print("Next Step: " + self.table[key][1].id)
  #       # print("\n")

  #   # If the host is not already in the table, add this data to the table.
  #   else:
  #     self.table[host] = [packet.current_weight, packet.current_router]


  # # Initialize new packet with this router as the destination and the flow dest
  # # as the source
  def initializeRouterMessages(self, event_queue, flows, links, time):

    # For every flow that exists, make a new packet with the flow dest as the
    # source for the packet and this router instance as the destination.
    # This message is then added to the buffer for the link connected to
    # flow destination (found using findLastLink)
    for i in range(len(flows)):
      # Initialize the message
      message = packet(i + 1, flows[i].dest, self, 'message', 64, flows[i].dest)
      # Append the flow destination to the route since that is where it starts
      message.route.append(flows[i].dest.id)
      # Choose the start time as the inputted time
      message.start_time = time
      # Find the last link
      last_link = flows[i].findLastLink(links)
      # Add the data to buffer for the last_link
      last_link.addToBuffer(event_queue, time, message, flows[i])

  def chooseNextDest(self, newPacket):
    dest = newPacket.destination

    # Get the data corresponding to this destination and choose the next router
    # from the data
    vals = self.table[dest]
    nextRouter = vals[1]

    return nextRouter
    




    

    

    
    
