import packet

class router:

  # This is defined globally for all instances of the router class
  # This is a dictionary of dictionaries for each host.
  globalTable = {}

  def __init__(self, id):
    self.id = id
    self.table = {}

  def updateTable(self, globalTable):
    for host in globalTable:
      routers = globalTable[host]
      self.table[host] = routers[self]

  def chooseNextDest(self, newPacket):
    dest = newPacket.destination
    nextRouter = self.table[dest]
    return nextRouter
    

    

    

    
    
