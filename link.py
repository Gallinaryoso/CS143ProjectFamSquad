import router
import packet
import event_queue

class link:
  
  def __init__(self, id, end_1, end_2, rate, delay, buffer_capacity):
    self.id = id
    self.end_1 = end_1
    self.end_2 = end_2
    self.rate = rate # in Mbps
    self.delay = delay # in ms 
    self.buffer_capacity = buffer_capacity # in KB
    self.buffer_occupancy = 0 # in bytes
    self.buffer_elements = [] # packets in the buffer
    
  def updateBuffer(self, event_queue, packet):
    if buffer_occupancy + packet.size \
        < buffer_capacity * 1000:
          buffer_occupancy += packet.size
          buffer_elements.append(packet)
          event_queue.insert_event(event('Buffering', packet.current_router, 
                                         packet, link))
