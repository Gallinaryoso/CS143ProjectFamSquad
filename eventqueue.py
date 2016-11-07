import heapq 

class Event: 
    def __init__(self, event_type, time):
        '''holder - we need to figure out every possible event type
        and how to deal with each specific case ''' 
        self.type = event_type
        self.time = time
  
class EventQueue: 
    def __init__(self): 
        self.queue = [] 
        self.queue_size = 0 
    
    def insert_event(self, event): 
        # event needs to be a (time, event) tuple to be sorted properly
        heapq.heappush(self.queue, (event.time, event))  
        self.queue_size += 1 
    
    def pop_event(): 
        if self.queue == 0: 
            #empty heap means we're done 
            return -1 
        popped = heapq.pop(self.queue)
        self.queue_size -= 1
        return popped 
  
   
    
           
           
           
