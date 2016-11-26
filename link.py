import router
import packet
from eventqueue import event_queue, event 

class link:
  
  def __init__(self, id, end_1, end_2, rate, delay, buffer_capacity):
    self.id = id #ID of link
    self.end_1 = end_1 #one end of link
    self.end_2 = end_2 #other end of link
    self.rate = rate # link transmission rate in Mbps
    self.delay = delay # link propagation time in ms 
    self.buffer_capacity = buffer_capacity # buffer capacity in KB
    self.buffer_occupancy = 0 # buffer occupancy in bytes
    self.buffer_elements = [] # list of packets in the buffer
  
  #update link buffer by adding a packet, only if the buffer is not filled
  def addToBuffer(self, event_queue, time, packet, flow):
    
    #check if the next packet wil not overfill the link buffer
    if self.buffer_occupancy + packet.size \
      < self.buffer_capacity * 1000:
      
        #add the packet to the buffer and update its occupancy and elements
        self.buffer_occupancy += packet.size
        self.buffer_elements.append(packet)
        
        #add the packet buffering event to the event queue
        event_queue.insert_event(event('Buffering', time, packet, self, flow))
        
    #if the buffer is overfilled, then the packet is dropped
    else:
      flow.occupancy -= 1
      
  #get the transmission time for a packet based on the link rate
  def getTransmission(self, packet):
    return packet.size * 8 / (self.rate * 1000000.)  
    
  #update all of the packet delays on a bufer when the first packet is removed
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
      self.buffer_elements[i].delay += transmission
      if switch != 0:
        self.buffer_elements[i].delay += self.delay / 1000.  
