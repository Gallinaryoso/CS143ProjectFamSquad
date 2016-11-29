from packet import packet 
from link import link
from router import router 
from flow import flow 
from eventqueue import event_queue, event
from main import *
import sys

def main(argv): 
	if len(sys.argv) != 4: 
		print "python ProjectSimulation.py (0,1,2) (0,1,2) (0,1)"
		print "1st arg: 0 - test_0; 1 - test_1; 2 - test_2"
		print "2nd arg: con_ctrl: 0 - none; 1 - TCP Reno; 2 - FAST"
		print "3rd arg: verbose: 0 - no; 1 - yes"

	else: 
		if int(sys.argv[1]) == 0: 
			test_0(int(sys.argv[2]), int(sys.argv[3]))
		if int(sys.argv[1]) == 1: 
			test_1(int(sys.argv[2]), int(sys.argv[3]))
		if int(sys.argv[1]) == 2: 
			test_2(int(sys.argv[2]), int(sys.argv[3]))

if __name__ == "__main__":
   main(sys.argv)