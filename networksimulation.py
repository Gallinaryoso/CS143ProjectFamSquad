from packet import packet 
from link import link
from router import router 
from flow import flow 
from eventqueue import event_queue, event
import shortestPath as sP
from run import *
import sys

def main(argv): 
	# Check command line parameters
	if len(sys.argv) != 3: 
		print "python ProjectSimulation.py (0,1,2) (0,1)"
		print "1st arg: con_ctrl: 0 - none; 1 - TCP Reno; 2 - FAST"
		print "2nd arg: verbose: 0 - no; 1 - yes"
		print('\n')
		sys.exit()

	# Store command line parameters
	con_ctrl = int(sys.argv[1])
	verbose = int(sys.argv[2])

	print('\n')
	# Give specifications for links file and flows file and then save
	# the filename in variables
	print("Enter the file of links.")
	print("Each line is one link in the following format: ")
	print("End1 End2 Rate Delay Capacity\n")
	print("Ends=host/source/destination/router ID (ex. H1,S2,T3,R4)")
	print("Rate(Mbps), Delay(ms), Capacity(KB)")
	linkFile = input('Enter link file: ')

	print('\n')
	print("Enter the file of flows.")
	print("Each line is one flow in the following format: ")
	print("Source Dest DataAmount StartTime\n")
	print("Source/Dest = ID's (ex. H1,S2,T3,R4)")
	print("DataAmount(MB), StartTime(s)")
	flowFile = input('Enter flow file: ')
	print('\n')

	# Variables to store the different network objects
	routers = {}
	linksLst = []
	flowsLst = []

	# Try to open the files. If fail, throw an error.
	try:
		links = open(linkFile, 'r')
		flows = open(flowFile, 'r')
	except IOError:
		print("Link and Flow files do not exist in this directory.")
		sys.exit()

	# First, make all the links
	i = 0
	for line in links:
		# Split the line into a list, which must have 5 values
		info = line.split(' ')
		if(len(info) != 5):
			print('Each link line must have 5 values')
			sys.exit()

		# Try converting the rate, delay and capacity. If fail, throw error
		try:
			rate, delay, capacity = float(info[2]), float(info[3]), float(info[4])
		except ValueError:
			print("The last 3 values must be numbers")
			sys.exit()

		# Either make a new entry in the routers table, or grab an entry

		# First get the end1 of the link
		if(info[0] not in routers.keys()):
			router1 = router(info[0])
			routers[info[0]] = router1
		else:
			router1 = routers[info[0]]

		# Next get end2
		if(info[1] not in routers.keys()):
			router2 = router(info[1])
			routers[info[1]] = router2
		else:
			router2 = routers[info[1]]

		# Build a link with all the information and add it to the list of links.
		temp = link(i, router1, router2, rate, delay, capacity)
		linksLst.append(temp)
		i += 1

	# Now, make all the flows.
	for line in flows:
		# Split the line into a list, which must have 4 values
		info = line.split(' ')
		if(len(info) != 4):
			print('Each flow line must have 4 values')
			sys.exit()

		# Try converting the amount and start time. If fail, throw error.
		try:
			amount, start = int(info[2]), float(info[3])
		except ValueError:
			print("The last 2 values must be numbers")
			sys.exit()

		# Try getting the source and dest from the dictionary. If they
		# don't exist, it means no link was connected to them, so we
		# can't have a flow.
		try:
			source = routers[info[0]]
			destination = routers[info[1]]
		except KeyError:
			print("Network not connected")
			sys.exit()

		# Build a flow with all the information and add it to the list of flows.
		temp = flow(source, destination, amount, start, con_ctrl)
		flowsLst.append(temp)

	# Make a list of all the routers using the routers dictionary.
	routersLst = []
	for key in routers:
		routersLst.append(routers[key])

	# intitialize an event queue
	the_event_queue = event_queue(verbose)

	# Statically initialize all the routing tables
	globalTable = sP.fillTable(linksLst, flowsLst)
	for fl in flowsLst:
		fl.src.updateStatic(globalTable)
	for rt in routersLst:
		rt.updateStatic(globalTable)

	# Start the simulation
	run_simulation(the_event_queue, flowsLst, linksLst, routersLst, con_ctrl)

if __name__ == "__main__":
   main(sys.argv)
