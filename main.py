import numpy as np
from packet import packet 
from link import link
import test 
from router import router 
from flow import flow 
from eventqueue import event_queue, event

data_packet_size = 1024 #bytes
data_ack_size = 64 #bytes

def startPropagating(popped_event, event_queue):
  transmission = popped_event.packet.size * 8 / \
                 (popped_event.link.rate * 10**6)
  popped_event.link.buffer_elements.remove(popped_event.packet)
  popped_event.link.buffer_occupancy -= popped_event.packet.size
  for i in range(len(popped_event.link.buffer_elements)):
    popped_event.link.buffer_elements[i].delay += transmission
    if popped_event.link.buffer_elements[0].current_router !=
      popped_event.packet.current_router:
        popped_event.link.buffer_elements[i].delay += \
          popped_event.link.delay
  event_queue.insert_event(event('Propagating', popped_event.time +
                                 popped_event.link.delay, 
                                 popped_event.packet, popped_event.link,
                                 popped_event.flow))
  
def run_simulation(event_queue, flows, links):
  
  #get sample router to start sending packets from to compute shortest path
  #sample_router = flow[0].src
  
  #add all of the packets for each flow, with the flow source put into route
  for flow in flows:
    packet_amount = (flow.amt * 10**6) / data_packet_size
    all_packets = [0] * packet_amount
    for i in range(packet_amount):
      all_packets[i] = packet(i + 1, flow.src, flow.dest, 'packet',
                              data_packet_size, flow.src)
      all_packets[i].route.append(flow.src.id)
    flow.packets = all_packets
    
  #set the initial window size
  window = 1
  
  #compute the shortest path to get initial routing tables
  #sample_router.computeShortestPath(links, event_queue)
  
  #initialize first link's buffer for each flow from host based on window size
  for i in range(len(flows)):
    for j in range(len(links)):
      if links[j].end_1 == flows[i].src or links[j].end_2 == flows[i].src
        first_link = links[j]
        break
     
    for k in range(window):
      transmission = flows[i].packets[k] * 8 / \
                 (first_link.rate * 10**6)
      first_link.updateBuffer(event_queue, flow.start + transmission,
                              flows[i].packets[k], flow)
      flow.current_packet += 1
     
  #iterate through all packets, using the same sequential events in the queue
  while not event_queue.is_empty():
  
    #get event after popping from queue
    popped_event = event_queue.pop_event()
    
    if popped_event.flow.current_packet <= len(popped_event.flow.packets):
    
      if popped_event.packet.delay > 0:
        event_queue.insert_event(event(popped_event.event_type, 
                                       popped_event.time + popped_event.packet.delay, 
                                       popped_event.packet, popped_event.link, 
                                       popped_event.flow))
        
      elif popped_event.event_type == 'Buffering':
        startPropagating(popped_event, event_queue)

      else:
        if popped_event.packet.type == 'ack' \
          and (popped_event.packet.current_router = popped_event.link.end_1 
            and popped_event.link.end_2 == flow.src) or
            (popped_event.packet.current_router = popped_event.link.end_2 
            and popped_event.link.end_1 == flow.src):
              new_packet = popped_event.flow.packets \
                           [popped_event.flow.current_packet - 1]
              for j in range(len(links)):
                if links[j].end_1 == popped_event.flow.src \
                  or links[j].end_2 == popped_event.flow.src:
                  first_link = links[j]                
              transmission = new_packet.size * 8 / \
                             (first_link.rate * 10**6)
              first_link.updateBuffer(event_queue, popped_event.time +
                                        transmission, new_packet, 
                                        popped_event.flow)
              popped_event.flow.current_packet += 1

        elif popped_event.packet.type == 'packet' \
          and popped_event.link.end_2 == flow.dest:
            ack = packet(popped_event.packet.id, flow.src, flow.dest, 
                         'ack', data_ack_size, flow.dest)

            ack.router += 1
            ack.route = popped_event.packet.route
            ack.route.append(flow.dest.id)
            ack.current_router = flow.dest

            popped_event.link.updateBuffer(event_queue, popped_event.time +
                                        transmission, ack,
                                        popped_event.flow)

        elif popped_event.packet.type == 'packet':
          next_link = links[0]
          for i in range(len(links)):
            if popped_event.current_router = popped_event.link.end_1:
              if links[i].end_1 == popped_event.link.end_2 \
                and links[i].end_2 == \
                popped_event.link.end_2.chooseNextDest(popped_event.packet):
                  next_link = links[i]
                  popped_event.packet.current_router = next_link.end_1
                  break
              elif links[i].end_2 == popped_event.link.end_2 \
                and links[i].end_1 == \
                popped_event.link.end_2.chooseNextDest(popped_event.packet):
                  next_link = links[i]
                  popped_event.packet.current_router = next_link.end_2
                  break

            elif popped_event.current_router = popped_event.link.end_2:
              if links[i].end_1 == popped_event.link.end_1 \
                and links[i].end_2 == \
                popped_event.link.end_1.chooseNextDest(popped_event.packet):
                  next_link = links[i]
                  popped_event.packet.current_router = next_link.end_1
                  break
              elif links[i].end_2 == popped_event.link.end_1 \
                and links[i].end_1 == \
                popped_event.link.end_1.chooseNextDest(popped_event.packet):
                  next_link = links[i]
                  popped_event.packet.current_router = next_link.end_2
                  break

          popped_event.packet.route.append(popped_event.current_router)
          popped_event.packet.router += 1
          transmission = popped_event.packet.size * 8 / \
                         (next_link.rate * 10**6)

          next_link.updateBuffer(event_queue, popped_event.time +
                                 transmission, popped_event.packet,
                                 popped_event.flow)

        else:
          next_link = links[0]
          for i in range(len(links)):
            if links[i].end_1 == \
            popped_event.packet.route[popped_event.packet.router - 1] \
              and (links[i].end_2 == popped_event.link.end_1 or
                   links[i].end_2 == popped_event.link.end_2):
                next_link = links[i]
                popped_event.packet.current_router = links[i].end_1 
                break
            elif links[i].end_2 = \
              and (links[i].end_1 == popped_event.link.end_1 or
                   links[i].end_1 == popped_event.link.end_2):
                next_link = links[i]
                popped_event.packet.current_router = links[i].end_2
                break

          popped_event.packet.router -= 1  

          next_link.updateBuffer(event_queue, popped_event.time +
                                 transmission, popped_event.packet,
                                 popped_event.flow)   

  #verify_packets(packets)

def test_0():
  
  #initialize event queue as empty
  the_event_queue = event_queue()
  
  #initialize the only two hosts as the routers
  host_1 = router('H1') 
  host_2 = router('H2')
  
  #create the one link
  link_1 = link(1, host_1, host_2, 10, 10, 64) 
  
  #create the one flow
  flow_1 = flow(host_1, host_2, 20, 1)
    
  # Create arrays for links and flows
  links = [link_1]
  flows = [flow_1]
    
  # Simulate all of the events on the event queue with input flows and links
  run_simulation(the_event_queue, flows, links)

def test_1():
  the_event_queue = event_queue() 

  host_1 = router('H1') 
  host_2 = router('H2')
  router_1 = router('R1')
  router_2 = router('R2')
  router_3 = router('R3')
  router_4 = router('R4')
  link_0 = link(0, host_1, router_1, 12.5, 10, 64) 
  link_1 = link(1, router_1, router_2, 10, 10, 64) 
  link_2 = link(2, router_1, router_3, 10, 10, 64) 
  link_3 = link(3, router_2, router_4, 10, 10, 64) 
  link_4 = link(4, router_3, router_4, 10, 10, 64) 
  link_5 = link(5, router_4, host_2, 12.5, 10, 64) 
  host_1.table = {host_2:router_1}
  router_1.table = {host_2:router_2}
  router_2.table = {host_2:router_4}
  router_3.table = {host_2:router_4}
  router_4.table = {host_2:host_2}

  flow_1 = flow(host_1, host_2, 20, 0.5)

  packet_amount = (flow_1.amt * 10**6) / data_packet_size
  packets = [0] * packet_amount
  for i in range(packet_amount):
    packets[i] = packet(i + 1, host_1, host_2, 'packet', data_packet_size)
    packets[i].route.append(flow_1.src.id)

  links = [link_0,link_1,link_2,link_3,link_4,link_5]
  flows = [flow_1]
  
  run_simulation(the_event_queue, flow_1, links, packets)

#test_0()
test_1() 

