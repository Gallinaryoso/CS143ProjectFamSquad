import numpy as np
from packet import packet 
from link import link
from router import router 
from flow import flow 
from eventqueue import event_queue, event

data_packet_size = 1024 #bytes
data_ack_size = 64 #bytes

def run_simulation(event_queue, flow, links, packets):
  
  #set the initial window size
  window = 1
  
  #use Dijkstra algorithm to get initial routing tables

  
  #initialize the packet closest from getting into the network flow
  current_packet = 1
  
  #initialize first link's buffer from host based on window size
  for i in range(len(links)):
    if links[i].end_1 == flow.src:
      first_link = links[i]
      break
      
  for j in range(window):
    if first_link.buffer_occupancy + data_packet_size \
      < first_link.buffer_capacity * 1000:
        first_link.buffer_occupancy += data_packet_size
        first_link.buffer_elements.append(packets[j])
        event_queue.insert_event(event('Buffering', flow.start, 
                                       packets[j], first_link))
    current_packet += 1
     
  #iterate through all packets, using the same sequential events in the queue
  i = 0 
  while not event_queue.is_empty() and i < 10:
    i += 1 
  
    popped_event = event_queue.pop_event()
    if popped_event.event_type == 'Buffering':
      transmission = popped_event.packet.size * 8 / \
                       (popped_event.link.rate * 10**6)
      popped_event.link.buffer_elements.remove(popped_event.packet)
      popped_event.link.buffer_occupancy -= popped_event.packet.size
      for k in range(len(popped_event.link.buffer_elements)):
        popped_event.link.buffer_elements[k].delay += transmission
      event_queue.insert_event(event('Propagating', popped_event.time +
                                     transmission + popped_event.packet.delay, 
                                     popped_event.packet, popped_event.link))
      popped_event.packet.delay = 0
    
    else:
      if popped_event.packet.size == data_ack_size \
        and popped_event.link.end_1 == flow.src:
          if current_packet != len(packets):
            if first_link.buffer_occupancy + data_packet_size \
              < first_link.buffer_capacity * 1000: # MB to KB 
                first_link.buffer_occupancy += data_packet_size
                first_link.buffer_elements.append(packets[current_packet - 1])
                event_queue.insert_event(event('Buffering', popped_event.time +
                                               popped_event.link.delay * 10**-3,
                                               packets[current_packet - 1], 
                                               first_link))
          current_packet += 1
          
      elif popped_event.packet.size == data_packet_size \
        and popped_event.link.end_2 == flow.dest:
          ack = packet(popped_event.packet.id, popped_event.link.end_1, 
                       popped_event.link.end_2, data_ack_size)
          
          ack.router += 1
          ack.route = popped_event.packet.route
          ack.route.append(flow.dest.id)
          
          if popped_event.link.buffer_occupancy + data_ack_size  \
            < popped_event.link.buffer_capacity * 1000:
              popped_event.link.buffer_occupancy += data_ack_size
              popped_event.link.buffer_elements.append(ack)              
              event_queue.insert_event(event('Buffering', popped_event.time +
                                       popped_event.link.delay * 10**-3,
                                       ack, popped_event.link))
          
      elif popped_event.packet.size == data_packet_size:
        next_link = links[0]
        for a in range(len(links)):
          if links[a].end_1 == popped_event.link.end_2 \
            and links[a].end_2 == \
            popped_event.link.end_2.chooseNextDest(popped_event.packet):
              next_link = links[a]
              break

        if next_link.buffer_occupancy + data_packet_size  \
          < next_link.buffer_capacity * 1000:
            next_link.buffer_occupancy += data_packet_size
            popped_event.link.buffer_elements.append(popped_event.packet)
            popped_event.packet.route.append(popped_event.link.end_2.id)
            popped_event.packet.router += 1
            event_queue.insert_event(event('Buffering', popped_event.time +
                                       popped_event.link.delay * 10**-3,
                                       popped_event.packet,
                                       next_link))
      else:
        next_link = links[0]
        for b in range(len(links)):
          if links[b].end_1 == \
          popped_event.packet.route[popped_event.packet.router - 1] \
            and links[b].end_2 == popped_event.link.end_1:
              next_link = links[b]
              break
          
        if next_link.buffer_occupancy + data_ack_size \
          < next_link.buffer_capacity * 1000:
            next_link.buffer_occupancy += data_ack_size
            popped_event.link.buffer_elements.append(popped_event.packet)
            popped_event.packet.router -= 1             
            event_queue.insert_event(event('Buffering', popped_event.time +
                                 popped_event.link.delay * 10**-3,
                                 popped_event.packet,
                                 next_link))                                 
    
def test_0():
  
  #define components used in network
  the_event_queue = event_queue() 
  host_1 = router('H1') 
  host_2 = router('H2')
  link_1 = link(1, host_1, host_2, 10, 10, 64) 
  flow_1 = flow(host_1, host_2, 20, 1)
  
  # Make a bunch of packets to store in an array
  packet_amount = (flow_1.amt * 10**6) / data_packet_size
  packets = [0] * packet_amount
  for i in range(packet_amount):
    packets[i] = packet(i + 1, host_1, host_2, data_packet_size)
    packets[i].route.append(flow_1.src.id)
  
  # Create array for links, assuming there is one flow for now
  links = [link_1]
  
  # Create event queue, in which events are sending, 
  # propagating, and acknowledging the packets
  run_simulation(the_event_queue, flow_1, links, packets)

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
    packets[i] = packet(i + 1, host_1, host_2, data_packet_size)
    packets[i].route.append(flow_1.src.id)

  links = [link_0,link_1,link_2,link_3,link_4,link_5]

  run_simulation(the_event_queue, flow_1, links, packets)

#test_0()
test_1() 

