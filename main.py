from packet import packet 
from link import link
import test 
from router import router 
from flow import flow 
from eventqueue import event_queue, event
import shortestPath as sP
import matplotlib.pyplot as plt

data_packet_size = 1024 #packet size in bytes
data_ack_size = 64 #acknowledgement size in bytes

#begin propagating a particular packet after buffering ends,
#updating the event time to be when progagation ends
def startPropagating(popped_event, event_queue, links):
  
  #update the flow rate when there is propagation in the flow's initial link
  if popped_event.link == popped_event.flow.findFirstLink(links):
    
    #if this is the first packet propagating, set the 'last propagation' time
    if popped_event.flow.last_propagation < 0:
      popped_event.flow.last_propagation = popped_event.time
      
    #else calculate the flow's rate and update the 'last propagation' time
    else:
      popped_event.flow.flow_rate = 8 * popped_event.packet.size / \
        ((popped_event.time - popped_event.flow.last_propagation) * 1000000.)
      popped_event.flow.last_propagation = popped_event.time
      
      #add the time point to the flow's rate history
      popped_event.flow.flow_rate_history.append((popped_event.time, 
        popped_event.flow.flow_rate))
      
  #add delay to relevant packets in the same link buffer when
  #the packet is transitioning from buffering to propagating
  popped_event.link.updateBufferPackets(popped_event.packet)
  
  #if this is the first packet propagating, set the link's 'last propagation'
  if popped_event.link.last_propagation < 0:
    popped_event.link.last_propagation = popped_event.time
        
  #else calculate the flow's rate and update the last propagation time
  else:
    popped_event.link.current_rate = 8 * popped_event.packet.size / \
      ((popped_event.time - popped_event.link.last_propagation) * 1000000.)
    popped_event.link.last_propagation = popped_event.time
    
    #add the time point to the link's rate history
    popped_event.link.link_rate_history.append((popped_event.time, 
        popped_event.link.current_rate))
  
  #insert the event of the packet propagating, adding the link delay time
  event_queue.insert_event(event('Propagating', popped_event.time +
                                 popped_event.link.delay / 1000., 
                                 popped_event.packet, popped_event.link,
                                 popped_event.flow))
  
  #if the window size is not filled in the flow, add a packet to the first link
  if popped_event.flow.occupancy < popped_event.flow.window:
    first_link = popped_event.flow.findFirstLink(links)  
    popped_event.flow.addPacket(event_queue, first_link, popped_event.time)
  
#run through the simulation by looking at each event in the event queue
def run_simulation(event_queue, flows, links):
  
  #get sample router to start sending packets from to compute shortest path
  #sample_router = flow[0].src
  
  #add all of the packets for each flow, with the flow source put into route
  for flow in flows:
    flow.initializePackets(data_packet_size)
  
  #compute the shortest path to get initial routing tables
  #sample_router.computeShortestPath(links, event_queue)
  
  #initialize first link's buffer for each flow from host based on window size
  for i in range(len(flows)):
    #get the first link connected to the flow's source
    first_link = flows[i].findFirstLink(links) 
     
    #fit however many packets into the first link and add buffering events
    for j in range(flows[i].window):
      flows[i].addPacket(event_queue, first_link, flows[i].start)
      
  #iterate through all packets, using the same sequential events in the queue
  while not event_queue.is_empty():
    #get event after popping from queue
    popped_event = event_queue.pop_event()
    #if there is congestion time for the popped packet, insert back into the
    #queue with the updated time and initialize packet delay back to 0
    if popped_event.packet.delay > 0:
      event_queue.insert_event(event(popped_event.event_type, 
                               popped_event.time + popped_event.packet.delay, 
                               popped_event.packet, popped_event.link, 
                               popped_event.flow))
      popped_event.packet.delay = 0
      continue
      
    #perform the transition from buffering to propagating
    elif popped_event.event_type == 'Buffering':
      startPropagating(popped_event, event_queue, links)
      
    #perform the transition from propagating to buffering
    else:
      #check whether the acknowledgment has returned to the source for a packet
      if popped_event.finishTrip() != 0:
          
          #update the packet delay for the flow when the RTT is finished
          popped_event.flow.packet_delay = (popped_event.time \
            - popped_event.packet.start_time) * 1000
          
          #add the time point to the flow's packet delay history
          popped_event.flow.packet_delay_history.append((popped_event.time, 
            popped_event.flow.packet_delay)) 
          
          #decrement the flow occupancy after packet finishes
          popped_event.flow.occupancy -= 1
          
          #if the last packet finishes, skip to the next event on queue
          if (popped_event.flow.current_packet 
              == len(popped_event.flow.packets) + 1):
            continue
          
          #get the first link of the flow to potentially add packets to
          first_link = popped_event.flow.findFirstLink(links)
          
          #while the occupancy has not reached the window, add packets to 
          #the first link if the link capacity is not met
          while popped_event.flow.occupancy < popped_event.flow.window:        
            popped_event.flow.addPacket(event_queue, first_link, 
                                        popped_event.time)       
           
      #check whether the packet has reached its destination
      elif popped_event.reachedDestination() != 0:
        
        #create an acknowledgement packet based on the popped packet's info
        ack = packet(popped_event.packet.id, popped_event.flow.src, 
                     popped_event.flow.dest, 'ack', data_ack_size, 
                     popped_event.flow.dest)
                
        #update the route and current router of this new acknowledgment packet
        ack.route_index = popped_event.packet.route_index
        ack.route = popped_event.packet.route
        ack.route.append(popped_event.flow.dest.id)
        ack.current_router = popped_event.flow.dest
        
        #make sure the start time of this ack is the corresponding packet's
        ack.start_time = popped_event.packet.start_time

        #calculate the transmission time of the acknowledgement to the event
        transmission = popped_event.link.getTransmission(ack)
        
        #add the buffering event of the new acknowledgement to the queue
        popped_event.link.addToBuffer(event_queue, popped_event.time +
                                    transmission, ack,
                                    popped_event.flow)

      #check if the packet is a packet routing in the middle of the flow
      elif popped_event.packet.type == 'packet':
        #route the packet and update the event queue 
        popped_event.routePacket(links, event_queue)

      #check if the packet is an acknowledgement and is not at the flow source
      elif popped_event.packet.type == 'ack' and \
        popped_event.packet.route_index > 0:
        #route the acknowledgement and update the event queue
        popped_event.routeAcknowledgement(links, event_queue)
    
    #get more time points for each link's occupancy and packet drops
    for i in range(len(links)):
      links[i].buffer_occupancy_history.append((popped_event.time, 
        links[i].buffer_occupancy))
      links[i].packet_drops_history.append((popped_event.time, 
        links[i].packet_drops))     
  
  print('Got here')
  flowNum = 0
  for i in range(len(flows)):
    #graph each flow's rate over time
    x,y = zip(*flows[i].flow_rate_history)
    # newX = []
    # newY = []
    # # Save every 100th point and plot it.
    # for i in range(0, len(x), 100):
    #   newX.append(x[i])
    #   newY.append(y[i])
    # plt.plot(newX,newY)
    plt.plot(x,y)
    plt.title('Flow Rate over Time for Flow ' + str(flowNum))
    plt.ylabel('Flow Rate')
    plt.xlabel('Time')
    plt.show()
    
    # #graph each flow's window size over time
    # plt.scatter(*zip(*flows[i].window_history))
    # plt.title('Flow Window Size over Time for Flow ' + str(flowNum))
    # plt.ylabel('Window Size')
    # plt.ylabel('Time')
    # plt.show() 
    
    # #graph each flow's packet delay over time
    # plt.scatter(*zip(*flows[i].packet_delay_history))
    # plt.title('Flow Packet Delay over Time for Flow ' + str(flowNum))
    # plt.ylabel('Packet Delay')
    # plt.ylabel('Time')
    # plt.show()  

    flowNum += 1
    
  for i in range(len(links)):
    #graph each link's rate over time
    plt.scatter(*zip(*links[i].link_rate_history))
    plt.title('Link Rate over Time for Link ' + str(links[i].id))
    plt.ylabel('Link Rate')
    plt.xlabel('Time')
    plt.show()
    
    #graph each link's buffer occupancy over time
    plt.scatter(*zip(*links[i].buffer_occupancy_history))
    plt.title('Link Buffer Occupancy over Time for Link ' + str(links[i].id))
    plt.ylabel('Buffer Occupancy')
    plt.xlabel('Time')
    plt.show() 
    
    #graph each link's packet drop count over time
    plt.scatter(*zip(*links[i].packet_drops_history))
    plt.title('Link Packet Drop Count over Time for Link ' + str(links[i].id))
    plt.ylabel('Packet Drop Count')
    plt.ylabel('Time')
    plt.show()    

def test_0():
  
  #initialize event queue as empty
  the_event_queue = event_queue()
  
  #initialize the only two hosts as routers
  host_1 = router('H1') 
  host_2 = router('H2')
  
  #create the one link
  link_1 = link(1, host_1, host_2, 10, 10, 64) 
  
  #create the one flow
  flow_1 = flow(host_1, host_2, 20, 1)
    
  #create arrays for links and flows
  links = [link_1]
  flows = [flow_1]
    
  #simulate all of the events on the event queue with input flows and links
  run_simulation(the_event_queue, flows, links)

def test_1():
  #initialize the event queue
  the_event_queue = event_queue() 

  #initialize the two hosts as routers
  host_1 = router('H1') 
  host_2 = router('H2')
  
  #create all four middle routers
  router_1 = router('R1')
  router_2 = router('R2')
  router_3 = router('R3')
  router_4 = router('R4')
  
  #create all 6 links
  link_0 = link(0, host_1, router_1, 12.5, 10, 64) 
  link_1 = link(1, router_1, router_2, 10, 10, 64) 
  link_2 = link(2, router_1, router_3, 10, 10, 64) 
  link_3 = link(3, router_2, router_4, 10, 10, 64) 
  link_4 = link(4, router_3, router_4, 10, 10, 64) 
  link_5 = link(5, router_4, host_2, 12.5, 10, 64) 
  
#   #create the update table for each router, for now
#   host_1.table = {host_2:router_1}
#   router_1.table = {host_2:router_2}
#   router_2.table = {host_2:router_4}
#   router_3.table = {host_2:router_4}
#   router_4.table = {host_2:host_2}

  # Create the list of hosts and list of links for the shortestPath functions.
  hosts = [host_1, host_2]
  links = [link_0, link_1, link_2, link_3, link_4, link_5]
  # Get the table of all paths to all hosts using the shortestPath fillTable
  # function.
  globalTable = sP.fillTable(links, hosts)

  # Update all the hosts/routers table
  host_1.updateTable(globalTable)
  router_1.updateTable(globalTable)
  router_2.updateTable(globalTable)
  router_3.updateTable(globalTable)
  router_4.updateTable(globalTable)
  host_2.updateTable(globalTable)

  ### Some Test Code
  # for key in host_1.table:
  #   print("Next Step to " + key.id + ": " + host_1.table[key].id)
  
  #create the one flow
  flow_1 = flow(host_1, host_2, 20, 0.5)

  #make arrays for the links and flows
  links = [link_0,link_1,link_2,link_3,link_4,link_5]
  flows = [flow_1]
  
  #simulate all of the events on the event queue with input flows and links
  run_simulation(the_event_queue, flows, links)
  
def test_2():
  #initialize the event queue
  the_event_queue = event_queue() 

  #initialize the 3 sources and 3 destinations (hosts)
  source_1 = router('S1') 
  source_2 = router('S2') 
  source_3 = router('S3') 
  dest_1 = router('T1')
  dest_2 = router('T2')
  dest_3 = router('T3')
  
  #create the 4 middle routers
  router_1 = router('R1')
  router_2 = router('R2')
  router_3 = router('R3')
  router_4 = router('R4')
  
  #create the 9 links
  link_0 = link(0, source_2, router_1, 12.5, 10, 128)
  link_1 = link(1, router_1, router_2, 10, 10, 128) 
  link_2 = link(2, router_2, router_3, 10, 10, 128) 
  link_3 = link(3, router_3, router_4, 10, 10, 128) 
  link_4 = link(4, router_1, source_1, 12.5, 10, 64) 
  link_5 = link(5, dest_2, router_2, 12.5, 10, 64) 
  link_6 = link(6, source_3, router_3, 12.5, 10, 64)
  link_7 = link(7, dest_1, router_4, 12.5, 10, 64)
  link_8 = link(8, dest_3, router_4, 12.5, 10, 64)

  hosts = [source_1, source_2, source_3, dest_1, dest_2, dest_3]
  links = [link_0, link_1, link_2, link_3, link_4, link_5, link_6, link_7, link_8]

  # Get the table of all paths to all hosts using the shortestPath fillTable
  # function.
  globalTable = sP.fillTable(links, hosts)

  # Update all the hosts/routers table
  source_1.updateTable(globalTable)
  source_2.updateTable(globalTable)
  source_3.updateTable(globalTable)
  dest_1.updateTable(globalTable)
  dest_2.updateTable(globalTable)
  dest_3.updateTable(globalTable)
  router_1.updateTable(globalTable)
  router_2.updateTable(globalTable)
  router_3.updateTable(globalTable)
  router_4.updateTable(globalTable)

  ### Some Test Code
  # for key in router_3.table:
  #   print("Next Step to " + key.id + ": " + router_3.table[key].id)
  
  # #initialize the routing tables for all routers, for now
  # source_1.table = {dest_1:router_1}
  # source_2.table = {dest_2:router_1}
  # source_3.table = {dest_3:router_3}
  # router_1.table = {dest_1:router_2, dest_2:router_2}
  # router_2.table = {dest_1:router_3, dest_2:dest_2}
  # router_3.table = {dest_1:router_4, dest_3:router_4}
  # router_4.table = {dest_1:dest_1, dest_3:dest_3}

  #create the 3 flows
  flow_1 = flow(source_1, dest_1, 35, 0.5)
  flow_2 = flow(source_2, dest_2, 15, 10)
  flow_3 = flow(source_3, dest_3, 30, 20)

  #create arrays for the links and flows
  links = [link_0, link_1, link_2, link_3, link_4,
           link_5, link_6, link_7, link_8]
  flows = [flow_1, flow_2, flow_3]
  
  #simulate all of the events on the event queue with input flows and links
  run_simulation(the_event_queue, flows, links)
  
# test_0()
# test_1() 
test_2()
