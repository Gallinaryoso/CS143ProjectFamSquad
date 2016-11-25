import packet

class router:
  
  def __init__(self, id):
    self.id = id
    self.table = {}
  
  # This static method iterates through all the links and finds
  # the ones that neighbor the inputted source.
  @staticmethod
  def getNeighborLinks(source, links):
    neighbors = []
    for link in links:
      # If either end of the link is the inputted source, it is a neighbor.
      if(link.end_2 == source or link.end_1 == source):
        neighbors.append(link)
    return neighbors
    
  def chooseNextDest(self, newPacket):
    dest = newPacket.destination
    nextRouter = self.table[dest]
    return nextRouter
    

    

    
    
