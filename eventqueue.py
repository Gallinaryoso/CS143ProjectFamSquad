import heapq 

class event: 
    def __init__(self, event_type, time):
        '''holder - we need to figure out every possible event type
        and how to deal with each specific case ''' 
        self.event_type = event_type
        self.time = time
  
class event_queue: 
    def __init__(self): 
        self.queue = [] 
        self.queue_size = 0 
    
    def insert_event(self, event): 
        # event needs to be a (time, event) tuple to be sorted properly
        heapq.heappush(self.queue, (event.time, event))  
        self.queue_size += 1 
    
    def pop_event(self): 
        if self.queue_size == 0: 
            #empty heap means we're done 
            return -1 
        popped = heapq.heappop(self.queue)[1]
        self.queue_size -= 1
        return popped 
           
           
           
