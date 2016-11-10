import numpy

import host.py
import packet.py
import link.py
import router.py
import flow.py
import event_queue.py 

data_packet_size = 1024
data_ack_size = 64

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
  
  # Create event queue, in which events are sending, 
  # propagating, and acknowledging the packets
  time_point = flow_1.start
  for i in range(packet_amount):
    packets[i] = packet('H1', 'H2')
    event_queue.insert_event(event('Sent', time_point))
    time_point += data_packet_size * 8 / link_1.rate + link_1.delay
    event_queue.insert_event(event('Propagated', time_point))
    time_point += data_ack_size * 8 / link1.rate + link1.delay
    event_queue.insert_event(event('Acknowledged', time_point))

def main():
  test_0()
