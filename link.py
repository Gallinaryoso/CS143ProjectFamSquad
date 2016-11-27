import router
import packet
from eventqueue import event_queue, event

class link:
  
  def __init__(self, id, end_1, end_2, rate, delay, buffer_capacity):
    self.id = id # ID of link
    self.end_1 = end_1 # one end of link
    self.end_2 = end_2 # other end of link
    self.rate = rate # maximum link transmission rate in Mbps
    self.delay = delay # link propagation time in ms
    self.last_propagation = -1 # the time when the last packet propagated
    self.current_rate = 0 # the current link rate in Mbps
    self.buffer_capacity = buffer_capacity # buffer capacity in KB
    self.buffer_occupancy = 0 # buffer occupancy in bytes
    self.buffer_elements = [] # list of packets in the buffer
    self.packet_drops = 0 # the number of accumulated packet drops at the link
    self.link_rate_history = [] # the link rate over time
    self.buffer_occupancy_history = [] # the buffer occupancy over time
    self.packet_drops_history = [] # the packet drop count over time
  
  #update link buffer by adding a packet, only if the buffer is not filled
  def addToBuffer(self, event_queue, time, packet, flow):
    
    #check if the next packet wil not overfill the link buffer
    if self.buffer_occupancy + packet.size \
      < self.buffer_capacity * 1000:
      
      #set the number of packet drops to 0
      self.packet_drops = 0
      
      #calculate the transmission time for the ack on this new link
      transmission = self.getTransmission(packet)
      
      #if there is delay from other packets in the buffer, delay this packet
      if len(self.buffer_elements) > 0 and time < \
         self.buffer_elements[len(self.buffer_elements) - 1].current_time: 
        
        #update the current time of the packet with delay in the buffer
        packet.current_time = self.buffer_elements[len(self.buffer_elements) \
          - 1].current_time
        
        #insert the buffering event for the new packet on the first link
        event_queue.insert_event(event('Buffering', packet.current_time, \
                                       packet, self, flow))
      else:
        #update the current time of the packet
        packet.current_time = time + transmission
        
        #add the packet buffering event to the event queue
        event_queue.insert_event(event('Buffering', time + transmission, \
                                       packet, self, flow))
        
      #add the packet to the buffer and update its occupancy and elements
      self.buffer_occupancy += packet.size
      self.buffer_elements.append(packet)      
        
    #if the buffer is overfilled, then the packet is dropped
    else:
      self.packet_drops += 1
      flow.occupancy -= 1
      
  #get the transmission time for a packet based on the link rate
  def getTransmission(self, packet):
    return packet.size * 8 / (self.rate * 1000000.)  
    
  #update all of the packet delays on a buffer when the first packet is removed
  def updateBufferPackets(self, packet):
    
    #get transmission time of link
    transmission = self.getTransmission(packet)
    
    #whether there the next link packet is at another router
    switch = self.buffer_elements[0].current_router != packet.current_router
    
    #remove the packet from the buffer, updating the buffer occupancy
    self.buffer_elements.remove(packet)
    self.buffer_occupancy -= packet.size
    
    #add packet delays, equal to the removed packet's propagation, if the  
    #half-duplex link has the next packet going the opposite direction
    for i in range(len(self.buffer_elements)):
      if self.buffer_elements[i].current_time \
        < packet.current_time + transmission:
        self.buffer_elements[i].current_time += transmission
      if switch != 0 and self.buffer_elements[i] < packet.current_time \
        + self.delay/1000.:
        self.buffer_elements[i].current_time += self.delay / 1000.  
