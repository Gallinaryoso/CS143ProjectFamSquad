import heapq 

class event: 
    def __init__(self, event_type, time, packet, link):
        '''holder - we need to figure out every possible event type
        and how to deal with each specific case ''' 
        self.event_type = event_type
        self.time = time
        self.packet = packet
        self.link = link
  
class event_queue: 
    def __init__(self): 
        self.queue = [] 
        self.queue_size = 0 
    
    def insert_event(self, event): 
        # event needs to be a (time, event) tuple to be sorted properly
        heapq.heappush(self.queue, (event.time, event))  
        self.queue_size += 1 
    
    def pop_event(self, verbose = False): 
        if self.is_empty():
            #empty heap means we're done 
            return -1 
        popped = heapq.heappop(self.queue)[1]
        self.queue_size -= 1
        verbose = True
        if verbose: 
            print "event: " + str(popped.event_type)
            print "time: " + str(popped.time)
            print "packet_id: " + str(popped.packet.id)
            print "packet size : " + str(popped.packet.size)
            print "current link end 1: " + str(popped.link.end_1.id)
            print "current link end 2: " + str(popped.link.end_2.id)
            print "source: " + str(popped.packet.source)
            print "destination: " + str(popped.packet.destination)
            print "route: " + str(popped.packet.route)
            print "\n"
        
        return popped 
    
    def is_empty(self):
        # If the queue is empty, return 1
        if self.queue_size == 0:
            return 1
           
           
           
