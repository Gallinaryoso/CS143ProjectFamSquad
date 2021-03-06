from eventqueue import event_queue, event
from packet import packet
from link import link

class flow:
  
  def __init__(self, src, dest, dataAMT, start, con_ctrl):
    self.src = src # source host of flow
    self.dest = dest # destination host of flow
    self.amt = dataAMT # amount of data in MB
    self.start = start # flow start time in seconds
    self.packets = [] # list of all packets needed in flow
    self.current_packet = 1 # index of packet that is next in line
    self.occupancy = 0 # how many packets are in the flow currently
    self.last_propagation = -1 # the time when the previous packet propagated
    self.flow_rate = 0 # the rate of packets going through the flow, in MB/s
    if con_ctrl == 0: 
      self.window = 50. # the number of packets supposed to be flowing
    if con_ctrl == 1 or con_ctrl == 2: 
      self.window = 1. 
      if con_ctrl == 1:
        self.ss_threshold = 9999999999
    self.packet_delay = 0 # the time it took for a packet to flow, in ms
    self.flow_rate_history = [] # the flow rate over time
    self.window_history = [] # the window size over time
    self.packet_delay_history = [] # the packet delay over time
    self.con_ctrl = con_ctrl
    self.base_rtt = 9999999999999
    self.last_rtt = 9999999999999999
    self.time_packet_last_seen = 9999999
    
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
      
  #get the last link of the flow, choosing from a list of links
  def findLastLink(self, links):

    #iterate through all links, with one link having one end as the flow dest
    for i in range(len(links)):
      if links[i].end_1 == self.dest or links[i].end_2 == self.dest:
        return links[i]

  #initializes a message for this flow with the message source as the flow
  #destination and the message destination as the flow source.
  #This message is then added to the buffer.
  def initializeMessage(self, event_queue, links, time):
      # Initialize the message
      message = packet(1, self.dest, self.src, 'message', 64, self.dest)
      # Append the flow destination to the route since that is where it starts
      message.route.append(self.dest.id)
      # Choose the start time as the inputted time
      message.start_time = time
      # Find the last link
      last_link = self.findLastLink(links)
      # Add the data to buffer for the last_link
      last_link.addToBuffer(event_queue, time, message, self)
  
  #add a packet to the first link based on the buffer occupancy
  def addPacket(self, event_queue, first_link, time):
    
    #check that there are still packets in the flow that need to be sent
    if self.current_packet <= len(self.packets):
      
      #access the next packet in the flow
      new_packet = self.packets[self.current_packet - 1]
      
      #check whether the buffer capacity allows for the packet to be added
      if first_link.buffer_occupancy + new_packet.size \
        < first_link.buffer_capacity * 1000:
        
        #set this next packet's start time
        new_packet.start_time = time
        
        #calculate the transmission time for the first link of the new packet
        transmission = first_link.getTransmission(new_packet) 
        
        #if there is delay from other packets in the buffer, delay this packet
        if len(first_link.buffer_elements) > 0:
          
          #get the last packet on the first link's buffer
          last = first_link.buffer_elements[len(first_link.buffer_elements) - 1]
          
          #check whether there is half-duplex congestion
          switch = last.current_router != new_packet.current_router \
             and last.type == 'packet'
          
          #if there is no half-duplex congestion, add transmission accordingly
          if switch == 0:
            if time < last.current_time:
              #set the current time of the new packet with link congestion
              new_packet.current_time = last.current_time + transmission             
            else:
              #set the current time of the new packet without link congestion
              new_packet.current_time = time + transmission
            
          #if there is half-duplex congestion, also add propagation accordingly
          else:
            if time < last.current_time:
              #set the current time of the new packet with link congestion
              new_packet.current_time = last.current_time + transmission + \
                first_link.rate / 1000.
            else:
              #set the current time of the new packet without link congestion
              new_packet.current_time = time + transmission
        else:
          new_packet.current_time = time + transmission
          
        #insert the buffering event for the new packet on the first link
        event_queue.insert_event(event('Buffering', new_packet.current_time,
                                       new_packet, first_link, self))
                  
        #append the packet to the link buffer and increase buffer occupancy
        first_link.buffer_occupancy += new_packet.size
        first_link.buffer_elements.append(new_packet)
        
        #update the current packet (not in the flow) and increment occupancy
        self.current_packet += 1
        self.occupancy += 1  
        
        #return 1 to indicate that a packet was added to the buffer
        return 1
      
      #return 0 to indicate that the buffer was too full to add a packet
      else:
        return 0
      
    #return 0 to indicate that there are no more packets for the flow
    else:
      return 0

