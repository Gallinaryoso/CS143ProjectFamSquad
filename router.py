import packet

class router:
  
  def __init__(self, id,):
    self.id = id
    self.table = {}
  
  def computeShortestPath(router, links):
  	return -1
  
  def chooseNextDest(self, newPacket):
    dest = newPacket.destination
    nextRouter = self.table[dest]
    return nextRouter
    

    

    
    
