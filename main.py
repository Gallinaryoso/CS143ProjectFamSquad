import sys
sys.path.insert(0, '/Downloads/numpy-1.11.2/numpy')
from packet import packet 
from link import link
import test 
from router import router 
from flow import flow 
from event_queue import event_queue, event

data_packet_size = 1024 #bytes
data_ack_size = 64 #bytes

def startPropagating(popped_event, event_queue):
  transmission = popped_event.packet.size * 8 / \
                 (popped_event.link.rate * 1000000.)
  popped_event.link.buffer_elements.remove(popped_event.packet)
  popped_event.link.buffer_occupancy -= popped_event.packet.size
  for i in range(len(popped_event.link.buffer_elements)):
    popped_event.link.buffer_elements[i].delay += transmission
    if popped_event.link.buffer_elements[0].current_router != \
      popped_event.packet.current_router:
        popped_event.link.buffer_elements[i].delay += \
          popped_event.link.delay
  event_queue.insert_event(event('Propagating', popped_event.time +
                                 popped_event.link.delay / 1000., 
                                 popped_event.packet, popped_event.link,
                                 popped_event.flow))
  
def run_simulation(event_queue, flows, links):
  
  #get sample router to start sending packets from to compute shortest path
  #sample_router = flow[0].src
  
  #add all of the packets for each flow, with the flow source put into route
  for flow in flows:
    packet_amount = (flow.amt * 1000000) / data_packet_size
    all_packets = [0] * packet_amount
    for i in range(packet_amount):
      all_packets[i] = packet(i + 1, flow.src, flow.dest, 'packet',
                              data_packet_size, flow.src)
      all_packets[i].route.append(flow.src.id)
    flow.packets = all_packets
    
  #set the initial window size
  window = 50
  
  #compute the shortest path to get initial routing tables
  #sample_router.computeShortestPath(links, event_queue)
  
  #initialize first link's buffer for each flow from host based on window size
  for i in range(len(flows)):
    for j in range(len(links)):
      if links[j].end_1 == flows[i].src or links[j].end_2 == flows[i].src:
        first_link = links[j]
        break
     
    for k in range(window):
      transmission = flows[i].packets[k].size * 8 / \
                 (first_link.rate * 1000000.)
      first_link.updateBuffer(event_queue, flows[i].start + transmission,
                              flows[i].packets[k], flows[i])
      flows[i].current_packet += 1

  #iterate through all packets, using the same sequential events in the queue
  while not event_queue.is_empty():
    #get event after popping from queue
    popped_event = event_queue.pop_event()
    
    if popped_event.flow.current_packet <= len(popped_event.flow.packets):
    
      if popped_event.packet.delay > 0:
        event_queue.insert_event(event(popped_event.event_type, 
                                       popped_event.time + 
                                       popped_event.packet.delay, 
                                       popped_event.packet, popped_event.link, 
                                       popped_event.flow))
        
      elif popped_event.event_type == 'Buffering':
        startPropagating(popped_event, event_queue)

      else:
        if popped_event.packet.type == 'ack' \
          and (popped_event.packet.current_router == popped_event.link.end_1 
            and popped_event.link.end_2 == popped_event.flow.src) or \
            (popped_event.packet.current_router == popped_event.link.end_2 
            and popped_event.link.end_1 == popped_event.flow.src):
              new_packet = popped_event.flow.packets \
                           [popped_event.flow.current_packet - 1]
              for j in range(len(links)):
                if links[j].end_1 == popped_event.flow.src \
                  or links[j].end_2 == popped_event.flow.src:
                  first_link = links[j]                
              transmission = new_packet.size * 8 / \
                             (first_link.rate * 1000000.)
              first_link.updateBuffer(event_queue, popped_event.time +
                                        transmission, new_packet, 
                                        popped_event.flow)
              popped_event.flow.current_packet += 1

        elif popped_event.packet.type == 'packet' \
          and (popped_event.packet.current_router == popped_event.link.end_1 
            and popped_event.link.end_2 == popped_event.flow.dest) or \
            (popped_event.packet.current_router == popped_event.link.end_2 
            and popped_event.link.end_1 == popped_event.flow.dest):
            ack = packet(popped_event.packet.id, popped_event.flow.src, 
                         popped_event.flow.dest, 'ack', data_ack_size, 
                         popped_event.flow.dest)

            ack.route_index = popped_event.packet.route_index
            ack.route = popped_event.packet.route
            ack.route.append(popped_event.flow.dest.id)
            ack.current_router = popped_event.flow.dest

            popped_event.link.updateBuffer(event_queue, popped_event.time +
                                        transmission, ack,
                                        popped_event.flow)

        elif popped_event.packet.type == 'packet':
          next_link = links[0]
          for i in range(len(links)):
            if popped_event.packet.current_router == popped_event.link.end_1:
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

            elif popped_event.packet.current_router == popped_event.link.end_2:
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

          popped_event.packet.route.append \
            (popped_event.packet.current_router.id)
          popped_event.packet.route_index += 1
          transmission = popped_event.packet.size * 8 / \
                         (next_link.rate * 1000000.)

          next_link.updateBuffer(event_queue, popped_event.time +
                                 transmission, popped_event.packet,
                                 popped_event.flow)

        elif popped_event.packet.route_index > 0:
          next_link = links[0]
          for i in range(len(links)):
            if links[i].end_1.id == \
            popped_event.packet.route[popped_event.packet.route_index - 1] \
              and (links[i].end_2 == popped_event.link.end_1 or
                   links[i].end_2 == popped_event.link.end_2):
                next_link = links[i]
                popped_event.packet.current_router = links[i].end_2
                break
            elif links[i].end_2.id == \
            popped_event.packet.route[popped_event.packet.route_index - 1] \
              and (links[i].end_1 == popped_event.link.end_1 or
                   links[i].end_1 == popped_event.link.end_2):
                next_link = links[i]
                popped_event.packet.current_router = links[i].end_1
                break

          popped_event.packet.route_index -= 1  

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

  links = [link_0,link_1,link_2,link_3,link_4,link_5]
  flows = [flow_1]
  
  run_simulation(the_event_queue, flows, links)
  
def test_2():
  the_event_queue = event_queue() 

  source_1 = router('S1') 
  source_2 = router('S2') 
  source_3 = router('S3') 
  dest_1 = router('T1')
  dest_2 = router('T2')
  dest_3 = router('T3')
  router_1 = router('R1')
  router_2 = router('R2')
  router_3 = router('R3')
  router_4 = router('R4')
  link_0 = link(0, source_2, router_1, 12.5, 10, 128)
  link_1 = link(1, router_1, router_2, 10, 10, 128) 
  link_2 = link(2, router_2, router_3, 10, 10, 128) 
  link_3 = link(3, router_3, router_4, 10, 10, 128) 
  link_4 = link(4, router_1, source_1, 12.5, 10, 64) 
  link_5 = link(5, dest_2, router_2, 12.5, 10, 64) 
  link_6 = link(6, source_3, router_3, 12.5, 10, 64)
  link_7 = link(7, dest_1, router_4, 12.5, 10, 64)
  link_8 = link(8, dest_3, router_4, 12.5, 10, 64)
  source_1.table = {dest_1:router_1}
  source_2.table = {dest_2:router_1}
  source_3.table = {dest_3:router_3}
  router_1.table = {dest_1:router_2, dest_2:router_2}
  router_2.table = {dest_1:router_3, dest_2:dest_2}
  router_3.table = {dest_1:router_4, dest_3:router_4}
  router_4.table = {dest_1:dest_1, dest_3:dest_3}

  flow_1 = flow(source_1, dest_1, 35, 0.5)
  flow_2 = flow(source_2, dest_2, 15, 10)
  flow_3 = flow(source_3, dest_3, 30, 20)

  links = [link_0, link_1, link_2, link_3, link_4,
           link_5, link_6, link_7, link_8]
  flows = [flow_1, flow_2, flow_3]
  
  run_simulation(the_event_queue, flows, links)
  
#test_0()
test_1() 
#test_2()
