import router
import packet
import event_queue

class link:
  
  def __init__(self, id, end_1, end_2, rate, delay, buffer_capacity):
    self.id = id #ID of link
    self.end_1 = end_1 #one end of link
    self.end_2 = end_2 #other end of link
    self.rate = rate # link transmission rate in Mbps
    self.delay = delay # link propagation time in ms 
    self.buffer_capacity = buffer_capacity # buffer capacity in KB
    self.buffer_occupancy = 0 # buffer occupancy in bytes
    self.buffer_elements = [] # list ot packets in the buffer
  
  #update link buffer by adding a packet, only if the buffer is not filled
  def updateBuffer(self, event_queue, packet):
    if buffer_occupancy + packet.size \
        < buffer_capacity * 1000:
          buffer_occupancy += packet.size
          buffer_elements.append(packet)
          event_queue.insert_event(event('Buffering', packet.current_router, 
                                         packet, link))
