from packet import packet
import shortestPath as sP
import sys

class router:

  # Initialize the router
  def __init__(self, id):
    self.id = id
    self.table = {}

  # This function parses through the statically created global table
  # in order to get the paths corresponding to this router for each
  # host.
  def updateStatic(self, globalTable):
    for host in globalTable.keys():
      subTable = globalTable[host]
      if(self in subTable.keys()):
        self.table[host] = subTable[self]
  
  # This function parses through the dynamically created dictionary in 
  # order to update this routers table.
  def updateTable(self, source, sDict):

    # Iterate through the router in the inputted dictionary
    for r in sDict.keys():
      if(r == self):
        # If r is the router, get the list of paths associated with it
        paths = sDict[r]
        # Find the best path (the path with the minimum weight, which is
        # the first term in the path)
        bestPath = paths[0]
        if(len(paths) > 1):
          bestPath = sP.findMinimumPath(paths)

        # If the source is already in the current routing table's keys, we
        # just need to update the table
        if(source in self.table.keys()):
          data = self.table[source]
          # If the best path's next step is the same as the existing next step,
          # update the weight
          if(bestPath[1] == data[1]):
            self.table[source][0] = bestPath[0]
          # If not the same next step, and the weight is less for the new path,
          # update the table
          elif(bestPath[0] < data[0]):
            self.table[source] = bestPath
        else:
          self.table[source] = bestPath

    #print(self.table)

  def chooseNextDest(self, newPacket):
    dest = newPacket.destination

    # Get the data corresponding to this destination and choose the next router
    # from the data
    vals = self.table[dest]
    nextRouter = vals[1]

    return nextRouter
    




    

    

    
    
