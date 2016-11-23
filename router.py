import packet

class router:
  
  def __init__(self, id):
    self.id = id
    self.table = {}
  
  def computeShortestPath(self, links):
  	numLinks = len(links)
  	for link in links:
  		bufCap = link.buffer_capacity


  	return -1
  
  def getNeighborLinks(self, links):
  	neighbors = []
  	for link in links:
  		if(link.end_1 == self or link.end_2 == self):
  			neighbors.append(link)
  	return neighbors
  
  def chooseNextDest(self, newPacket):
    dest = newPacket.destination
    nextRouter = self.table[dest]
    return nextRouter
    

    

    
    
