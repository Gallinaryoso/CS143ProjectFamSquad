import numpy

import host.py
import packet.py
import link.py
import router.py
import flow.py
import event_queue.py 

data_packet_size = 1024
data_ack_size = 64

def fill_event_queue(event_queue, flow, links, packet_amount):
  
  time_point = flow.start
  computeShortestPath(flow.src)
  current_router = flow.src
  for i in range(packet_amount):
    event_queue.insert_event(event('Sent', time_point))
    
    while current_router != flow.dest:
      next_router = current_router[flow.dest]
      for k in range(links):
        if (links[k].end_1 == current_router && links[k].end_2 == next_router):
          current_link = links[k]
          break
        
    time_point += data_packet_size * 8 / current_link.rate + current_link.delay
    event_queue.insert_event(event('Propagated', time_point))
    time_point += data_ack_size * 8 / current_link.rate + current_link.delay
    event_queue.insert_event(event('Acknowledged', time_point))
    
def test_0():
  
  #define components used in network
  event_queue = event_queue() 
  host_1 = router('H1', 1) 
  host_2 = router('H2', 1)
  link_1 = link(1, host_1, host_2, 10, 10, 64) 
  flow_1 = flow(host_1, host_2, 20, 1)
  
  # Make a bunch of packets to store in an array
  packet_amount = (flow_1.dataAMT * 10**6) / data_packet_size
  packets = empty(packet_amount)
  for i in range(packet_amount):
    packets[i] = packet('H1', 'H2')
  
  # Create array for links, assuming there is one flow for now
  links = empty(1)
  links[0] = link_1
  # Create event queue, in which events are sending, 
  # propagating, and acknowledging the packets
  fill_event_queue(event_queue, flow_1, links, packet_amount)

def main():
  test_0()
