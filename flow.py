from eventqueue import event_queue, event
from packet import packet
from link import link

class flow:
  
  def __init__(self, src, dest, dataAMT, start):
    self.src = src # source host of flow
    self.dest = dest # destination host of flow
    self.amt = dataAMT # amount of data in MB
    self.start = start # flow start time in seconds
    self.packets = [] # list of all packets needed in flow
    self.current_packet = 1 # index of packet that is next in line
    self.occupancy = 0 #how many packets are in the buffer currently
    self.window = 100 #the number of packets supposed flowing at this time
    
  #initialize all the packets in the flow based on the data amount
  def initializePackets(self, data_packet_size):
    
    #get the number of packets needed based on the data amount
    packet_amount = (self.amt * 1000000) / data_packet_size
    
    #fill the packets of the flow, setting the current route as just the source
    self.packets = [0] * packet_amount
    for i in range(packet_amount):
      self.packets[i] = packet(i + 1, self.src, self.dest, 'packet',
                              data_packet_size, self.src)
      self.packets[i].route.append(self.src.id)  
      
  #get the first link of the flow, choosing from a list of links
  def findFirstLink(self, links):
    
    #iterate through all links, with one link having one end as the flow source
    for i in range(len(links)):
      if links[i].end_1 == self.src or links[i].end_2 == self.src:
        return links[i] 
      
  #add a packet to the first link based on the buffer occupancy
  def addPacket(self, event_queue, first_link, time):
    
    #choose the next packet not in the flow
    new_packet = self.packets[self.current_packet - 1]
    
    #calculate the transmission time for the first link of the new packet
    transmission = first_link.getTransmission(new_packet)

    #check whether the buffer capacity allows for the packet to be added
    if first_link.buffer_occupancy + new_packet.size \
      < first_link.buffer_capacity * 1000:
      
      #append the packet to the link buffer and increase buffer occupancy
      first_link.buffer_occupancy += new_packet.size
      first_link.buffer_elements.append(new_packet)
      
      #insert the buffering event for the new packet on the first link
      event_queue.insert_event(event('Buffering', time + transmission,
                                     new_packet, first_link, self))
      
      #update the current packet (not in the flow) and increment flow occupancy
      self.current_packet += 1
      self.occupancy += 1      
