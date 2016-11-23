import numpy as np
import matplotlib.pyplot as plt
from packet import packet 
from link import link
from router import router 
from flow import flow 
from eventqueue import event_queue, event

def test_packets(packets):
  x = []
  y = []
  i = 0 
  for p in packets:  
    x.append(p.left_source)
    y.append(p.arrived_at_dest - p.left_source)
    if p.route != ['H1', 'R1', 'R2', 'R4', 'H2'] and p.size == data_packet_size:
      print p.route
      i += 1
    print i 
    print x
    print y 
    plt.plot(x,y)
    plt.show()
