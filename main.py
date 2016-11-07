import host.py
import packet.py
import link.py
import router.py
import flow.py
import event_queue.py 

def test_0():
  event_queue = event_queue() 
  host_1 = router(1, 1) 
  host_2 = router(2, 1)
  link_1 = link(1, host_1, host_2, 10, 10, 64) 
  flow_1 = flow(host_1, host_2, 20, 1) 
  

def main():
  # Make a bunch of packets
  # Add events to queue
  
  
  
