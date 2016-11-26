import sys  

# This module contains the functions needed to compute the shortest path.
# To do this, a table of every path to every destination is created.
# The router class contains a function (updateTable) to go through this 
# global table of all paths and find the ones that should be in the routing
# table for that router.

# This static method iterates through all the links and finds
# the ones that neighbor the inputted source.

def getNeighborLinks(source, links):
  neighbors = []
  for link in links:
    # If either end of the link is the inputted source, it is a neighbor.
    if(link.end_2 == source or link.end_1 == source):
      neighbors.append(link)
  return neighbors

# This method takes in a list of lists and outputs the list with the minimum
# weight. The weight is always the first element in the list.

def findMinimumPath(paths):
  minPath = paths[0]
  minWeight = minPath[0]

  for path in paths:

    if(path[0] < minWeight):
      minWeight = path[0]
      minPath = path

    # If the paths have the same weight, we favor the one with the smaller
    # length.
    elif(path[0] == minWeight):
      if(len(path) < len(minPath)):
        minPath = path

  return minPath

# This method takes in a dictionary of all paths from each router to the
# host. This changes the values in this dictionary to single router/host 
# objects representing the next step in the best path.

def minimizeDict(hostDict):
  for router in hostDict:
    paths = hostDict[router]
    bestPath = findMinimumPath(paths)
    hostDict[router] = bestPath[len(bestPath) - 1]

# This function fills up the dictionary with all the paths for every router

def computePath(source, links, hostDict, visited):
  # Base case: if the source has already been visited or contains 'H', 
  # meaning it is an endpoint, return an empty list.
  if(source in visited):
    return []

  # Gets the neighbors of the current source and then appends it to visited.
  neighbors = getNeighborLinks(source, links)
  visited.append(source)

  for link in neighbors:

    # Compute the weight of this new link
    weight = link.buffer_occupancy/float(link.buffer_capacity * 1000)

    # Find the other end of this link
    if(link.end_1 == source):
      newSource = link.end_2
    else:
      newSource = link.end_1

    # If this source isn't already a member of the dictionary, add it
    # it with the all paths from the source it came from plus the source.
    if(newSource not in hostDict.keys()):
      hostDict[newSource] = []
      paths = hostDict[source]
      for path in paths:

        # Copying
        temp = []
        for i in path:
          temp.append(i)

        # Adjusting
        temp.append(source)
        temp[0] += weight
        hostDict[newSource].append(temp)

    if(newSource not in visited):

      # Recursively call this function withthe newSource
      newPaths = computePath(newSource, links, hostDict, visited)

      # Ensure that an empty list wasn't returned
      if(len(newPaths) != 0):
        # Iterate through all the paths. If the current source is not in the
        # path, add the newSource to the end of it (since that is what
        # connects to the current source) and then adjust the weight.
        # Then, add this updated path to the list of paths for this source.
        # If the current source is in the path, do nothing since we don't
        # want any cycles.
        for path in newPaths:
          if(source not in path):
              # Copying
              temp = []
              for i in path:
                temp.append(i)

              # Adjusting
              temp.append(newSource)
              temp[0] += weight
              if(temp not in hostDict[source]):
                hostDict[source].append(temp)

    # If the new source is already in the dictionary
    elif(newSource in hostDict.keys()):
      # Get all the paths for that source
      oldPaths = hostDict[newSource]
      # Iterate through the paths and confirm the source is not in the path.
      # Adjust the path and add it to the list of paths for this source.
      for path in oldPaths:
        if(source not in path):
            # Copying
            temp = []
            for i in path:
              temp.append(i)

            # Adjusting
            temp.append(newSource)
            temp[0] += weight
            if(temp not in hostDict[source]):
              hostDict[source].append(temp)

  return hostDict[source]

# This function fills the globalTable.

def fillTable(links, hosts):

  globalTable = {}

  # Iterates through all the hosts (endpoints)
  for host in hosts:

    # Initializes a dictionary for this host. It will ultimately contain
    # all the paths from each router to the host.
    hostDict = {}

    # Gets the neighbors of the host and ensures there aren't multiple.
    neighbors = getNeighborLinks(host, links)

    if(len(neighbors) > 1):
      print("Network Error: Host has multiple links")
      sys.exit()

    # This saves the other end of the connected link in the newSource 
    # variable and then passes it to the computePath function.
    link = neighbors[0]
    if(link.end_1 == host):
      newSource = link.end_2
    else:
      newSource = link.end_1

    weightInit = link.buffer_occupancy/float(link.buffer_capacity * 1000)
    hostDict[newSource] = [[weightInit, host]]
    visited = [host]

    computePath(newSource, links, hostDict, visited)
    hostDict[host] = [[0, host]]

    minimizeDict(hostDict)
    globalTable[host] = hostDict
    
  return globalTable
