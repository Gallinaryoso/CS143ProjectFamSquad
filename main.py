import numpy

import host.py
import packet.py
import link.py
import router.py
import flow.py
import event_queue.py 

data_packet_size = 1024 #bytes
data_ack_size = 64 #bytes

def run_simulation(event_queue, flow, links, packets):
  
  #set the initial window size
  window = 1
  
  #use Dijkstra algorithm to get initial routing tables
  computeShortestPath(flow.src)
  
  #initialize the packet closest from getting into the network flow
  current_packet = 1
  
  #initialize first link's buffer from host based on window size
  for i in range(links):
    if links[i].end_1 == flow.src:
      first_link = links[i]
      break
      
  for j in range(window):
    if first_link.buffer_occupancy + data_packet_size 
         < first_link.buffer_capacity:
        first_link.buffer_occupancy += data_packet_size
        first_link.buffer_elements.append(packets[current_packet])
        event_queue.insert_event(event('Buffering', flow_start, 
                                       packets[j], first_link))
    current_packet += 1
     
  #iterate through all packets, using the same sequential events in the queue
  while not event_queue.isEmpty():
  
    popped_event = event_queue.pop_event()
    if popped_event.event_type == 'Acknowledging':
      #insert the event that the packet gets sent if there are still packets
      if current_packet != len(packets):
        if first_link.buffer_occupancy + data_packet_size 
         < first_link.buffer_capacity:
          first_link.buffer_occupancy += data_packet_size
          first_link.buffer_elements.append(packets[current_packet])
          event_queue.insert_event(event('Buffering', popped_event.time, 
                                         packets[current_packet - 1]), first_link)
        current_packet += 1
    
    else if popped_event.event_type == 'Buffering':
      transmission = popped_event.packet.size * 8 / 
                       popped_event.link.rate
      for k in range(len(popped_event.link.buffer_elements)):
        popped_event.link.buffer_elements[k].delay += transmission_time
      event_queue.insert_event(event('Propagating', popped_event.time +
                                     transmission + popped_event.packet.delay, 
                                     popped_event.packet, popped_event.link))
    
    else:
      if popped_event.packet_size == data_ack_size
        and popped_event.link.end_1 == flow.src:
          event_queue.insert_event(event('Acknowledging', popped_event.time + 
                                         popped_event.link.delay,
                                         popped_event.packet, 
                                         popped_event.link))
          
      else if popped_event.packet_size == data_packet_size
        and popped_event.link.end_2 == flow.dest:
          ack = packet(popped_event.link.end_1, popped_event.link.end_2, 
                       data_ack_size)
          event_queue.insert_event(event('Buffering', popped_event.time +
                                         popped_event.link.delay,
                                         ack, popped_event.link))
          
      else if popped_event.packet_size == data_packet_size
        for a in range(len(links)):
          if links[a].end_1 == popped_event.link.end_2
            and links[a].end_2 == popped_event.link.end_2.
                                  chooseNextDest(popped_event.packet):
              next_link = links[a]
              break
              
          if next_link.buffer_occupancy + data_packet_size 
            < next_link.buffer_capacity:
              next_link.buffer_occupancy += data_packet_size
              popped_event.packet.route.append(popped_event.link.end_2)
              popped_event.packet.router += 1

        event_queue.insert_event(event('Buffering', popped_event.time +
                                       popped_event.link.delay,
                                       popped_event.packet,
                                       next_link))
      else:
        for b in range(len(links)):
          packet.router -= 1
          if links[b].end_1 == popped_event.packet.route
                                 [popped_event.packet.router - 1]
            and links[b].end_2 == popped_event.link.end_1
              next_link = links[b]
              break
          
          if next_link.buffer_occupancy + data_packet_size 
            < next_link.buffer_capacity:
              next_link.buffer_occupancy += data_packet_size
              popped_event.packet.router -= 1
              
          event_queue.insert_event(event('Buffering', popped_event.time +
                                 popped_event.link.delay,
                                 popped_event.packet,
                                 next_link))                                 
    
def test_0():
  
  #define components used in network
  event_queue = event_queue() 
  host_1 = router('H1') 
  host_2 = router('H2')
  link_1 = link(1, host_1, host_2, 10, 10, 64) 
  flow_1 = flow(host_1, host_2, 20, 1)
  
  # Make a bunch of packets to store in an array
  packet_amount = (flow_1.dataAMT * 10**6) / data_packet_size
  packets = empty(packet_amount)
  for i in range(packet_amount):
    packets[i] = packet('H1', 'H2')
    packets[i].route.append(flow_1.src)
  
  # Create array for links, assuming there is one flow for now
  links = empty(1)
  links[0] = link_1
  
  # Create event queue, in which events are sending, 
  # propagating, and acknowledging the packets
  fill_event_queue(event_queue, flow_1, links, packets)

def main():
  test_0()
