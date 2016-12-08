import heapq 
from packet import packet
import sys

class event: 
    def __init__(self, event_type, time, packet, link, flow):
        '''holder - we need to figure out every possible event type
        and how to deal with each specific case ''' 
        self.event_type = event_type #the type of the event
        self.time = time #the time when event occurs
        self.packet = packet #the packet the event is relevant for
        self.link = link #the link the event is relevant for
        self.flow = flow #the flow the event is relevant for
    
    #true if the packet has reached the destination, false otherwise
    def reachedDestination(self):
        return self.packet.type == 'packet' \
          and (self.packet.current_router == self.link.end_1 
          and self.link.end_2 == self.flow.dest) or \
          (self.packet.current_router == self.link.end_2 
          and self.link.end_1 == self.flow.dest)   
    
    #true if the acknowledgement has reached the source, false otherwise
    def finishTrip(self):
        if self.packet.type != 'message':
            self.flow.last_rtt = (self.time - self.packet.start_time) 
            if self.flow.last_rtt < self.flow.base_rtt: 
                self.flow.base_rtt = self.flow.last_rtt
        return self.packet.type == 'ack' \
          and (self.packet.current_router == self.link.end_1 
          and self.link.end_2 == self.flow.src) or \
          (self.packet.current_router == self.link.end_2 
          and self.link.end_1 == self.flow.src)

    #true if the message has reached the source, false otherwise.
    def messageReceived(self, flow, links):
        first_link = flow.findFirstLink(links)
        return self.packet.type == 'message' and \
            (self.packet.current_router == first_link.end_1 or \
                self.packet.current_router == first_link.end_2)
    
    #move the packet to the next router, updating the next link and event queue
    def routePacket(self, links, event_queue):
        #initialize the next link where the packet should go
        next_link = links[0]
        
        #iterate through all links to find the packet's next link
        for i in range(len(links)):
            
            #check if the packet is currently at end 1 of its link 
            if self.packet.current_router == self.link.end_1:
                
                #check if a link has end 1 at the next router for the
                #packet and end 2 at the designated next link's other router
                if links[i].end_1 == self.link.end_2 \
                and links[i].end_2 == \
                self.link.end_2.chooseNextDest(self.packet):    
                    
                    #set the next link and update the packet's current router
                    next_link = links[i]
                    self.packet.current_router = next_link.end_1
                    break
                
                #check if a link has end 2 at the next router for the
                #packet and end 1 at the designated next link's other router                
                elif links[i].end_2 == self.link.end_2 \
                and links[i].end_1 == \
                self.link.end_2.chooseNextDest(self.packet):
                    
                    #set the next link and update the packet's current router
                    next_link = links[i]
                    self.packet.current_router = next_link.end_2
                    break

            #check if the packet is currently at end 2 of its link 
            elif self.packet.current_router == self.link.end_2:
                
                #check if a link has end 1 at the next router for the
                #packet and end 2 at the designated next link's other router                
                if links[i].end_1 == self.link.end_1 \
                and links[i].end_2 == \
                self.link.end_1.chooseNextDest(self.packet):
                    
                    #set the next link and update the packet's current router
                    next_link = links[i]
                    self.packet.current_router = next_link.end_1
                    break
                
                #check if a link has end 2 at the next router for the
                #packet and end 1 at the designated next link's other router                 
                elif links[i].end_2 == self.link.end_1 \
                and links[i].end_1 == \
                self.link.end_1.chooseNextDest(self.packet):
                    
                    #set the next link and update the packet's current router
                    next_link = links[i]
                    self.packet.current_router = next_link.end_2
                    break

        #update the route of the packet to include its next router
        self.packet.route.append(self.packet.current_router.id)
        self.packet.route_index += 1
        
        #calculate the transmission time for the packet on this new link
        transmission = next_link.getTransmission(self.packet)
        
        #add the packet to the next link's buffer, updating its occupancy
        next_link.addToBuffer(event_queue, self.time, self.packet,
                               self.flow)  
    
    #move the ack to the next router, updating the next link and event queue    
    def routeAcknowledgement(self, links, event_queue):
        #initialize the next link where the acknowledgement should go
        next_link = links[0]

        #iterate through all links to find the ack's next link        
        for i in range(len(links)):
            
            #check if the current router is at end 1 of its link
            if self.packet.current_router == self.link.end_1:
                
                #check if end 1 of a link is at end 2 of the ack's link and
                #end 2 of that link is at the ack's next link's other router
                if links[i].end_1 == self.link.end_2 and links[i].end_2.id == \
                self.packet.route[self.packet.route_index - 1]:  
                    
                    #set the next link and update the ack's current router
                    next_link = links[i]
                    self.packet.current_router = links[i].end_1
                    break
                
                #check if end 2 of a link is at end 2 of the ack's link and
                #end 1 of that link is at the ack's next link's other router                
                elif links[i].end_2 == self.link.end_2 \
                and links[i].end_1.id == \
                self.packet.route[self.packet.route_index - 1]:
                    
                    #set the next link and update the ack's current router
                    next_link = links[i]
                    self.packet.current_router = next_link.end_2
                    break
                
            #check if the current router is at end 2 of its link             
            elif self.packet.current_router == self.link.end_2:
                
                #check if end 1 of a link is at end 2 of the ack's link and
                #end 2 of that link is at the ack's next link's other router                
                if links[i].end_1 == self.link.end_1 \
                and links[i].end_2.id == \
                self.packet.route[self.packet.route_index - 1]:
                    
                    #set the next link and update the ack's current router
                    next_link = links[i]
                    self.packet.current_router = next_link.end_1
                    break
                
                #check if end 2 of a link is at end 2 of the ack's link and
                #end 1 of that link is at the ack's next link's other router                
                elif links[i].end_2 == self.link.end_1 \
                and links[i].end_1.id == \
                self.packet.route[self.packet.route_index - 1]:
                    
                    #set the next link and update the ack's current router
                    next_link = links[i]
                    self.packet.current_router = next_link.end_2
                    break          
        
        #decrement the route index of the ack to backtrack its route
        self.packet.route_index -= 1  

        #add the ack to the next link's buffer, updating its occupancy
        next_link.addToBuffer(event_queue, self.time, self.packet, self.flow) 

    # move the message to the next router, updating the next link and event queue 
    # This function also updates the packets dictionary of paths before sending 
    # it on each connected link   
    def routeMessage(self, links, event_queue):

        # This stores the weight of the current link in order to update
        # the weight of a message we forward.
        currentLinkWeight = \
            self.link.buffer_occupancy/float(self.link.buffer_capacity * 1000)

        #iterate through all links to find all connected links.  
        # For every connected link, make a new event that tries to get to the
        # same destination. 
        for i in range(len(links)):
            # Indicates that a new link to send a packet along was found.
            found = 0

            next_link = links[i]

            # Make a new copy of all the values in this event.
            time = self.time
            # Make a new packet with the same details as the old packet
            newMessage = packet(self.packet.id+1, self.packet.source, \
                self.packet.destination, self.packet.type, self.packet.size, \
                self.packet.current_router)

            # Copy over the packets route
            for i in self.packet.route:
                newMessage.route.append(i)

            # Copy the route index
            newMessage.route_index = self.packet.route_index

            # Copy over the current weight
            newMessage.current_weight = self.packet.current_weight
            
            flow = self.flow
        
            # Check if each link's end_1 is the same as the packets
            # current router.
            if(self.packet.current_router == self.link.end_1):

                #check if a link is connected, but isn't the same link
                if(next_link.end_1 == self.link.end_2 and \
                    next_link.end_2.id not in newMessage.route):

                    # Updates the message's current router
                    newMessage.current_router = next_link.end_1
                    found = 1

                #check if a link is connected, but isn't the same link
                elif(next_link.end_2 == self.link.end_2 and \
                    next_link.end_1.id not in newMessage.route):

                    # Updates the message's current router
                    newMessage.current_router = next_link.end_2
                    found = 1

            #check if the packet is currently at end 2 of its link
            elif(self.packet.current_router == self.link.end_2):

                #check if a link is connected, but isn't the same link
                if(next_link.end_1 == self.link.end_1 and \
                    next_link.end_2.id not in newMessage.route):

                    # Updates the message's current router
                    newMessage.current_router = next_link.end_1
                    found = 1

                #check if a link is connected, but isn't the same link
                elif(next_link.end_2 == self.link.end_1 and \
                    next_link.end_1.id not in newMessage.route):

                    # Updatesthe message's current router
                    newMessage.current_router = next_link.end_2
                    found = 1

            # If a new link has been found to project the packet onto, 
            # initializes all the necessary information and then add the event
            # to the buffer.
            if(found):
                # Update the message's route with the new current router
                newMessage.route.append(newMessage.current_router.id)
                # Updates the route index
                newMessage.route_index += 1
                # Update the message's weight
                newMessage.current_weight += currentLinkWeight

                # Add the current router as a new key to the packet's dictionary
                # and the path that it took to get there from the source, along
                # with the weight of the path as the value.
                currentRouter = self.packet.current_router
                newRouter = newMessage.current_router
                # If the router isn't in the dictionary:
                if(newRouter in self.packet.destDict.keys()):
                    lst = [newMessage.current_weight, currentRouter]
                    # If the list isn't in the dictionary:
                    if(lst not in self.packet.destDict[newRouter]):
                        self.packet.destDict[newRouter].append(lst)
                else:
                    self.packet.destDict[newRouter] = \
                        [[newMessage.current_weight, currentRouter]]

                # Update the new message dictionary with the newly updated one.
                newMessage.destDict = self.packet.destDict

                #add the packet to the next link's buffer, updating its occupancy
                next_link.addToBuffer(event_queue, time, newMessage, flow)

class event_queue: 
    def __init__(self, verbose): 
        self.queue = [] 
        self.queue_size = 0 
        self.verbose = verbose
    
    #insert an event to the queue
    def insert_event(self, event): 
        #event needs to be a (time, event) tuple to be sorted properly
        heapq.heappush(self.queue, (event.time, event))  
        
        #increment the event queue size
        self.queue_size += 1 
    
    #pop event from the queue
    def pop_event(self): 
        
        #empty heap means we're done
        if self.is_empty(): 
            return -1 
        
        #pop from the queue and decrement the queue size
        popped = heapq.heappop(self.queue)[1]
        self.queue_size -= 1
        
        # if verbose, print all of the info about the popped event
        if self.verbose != 0: 
            print "event: " + str(popped.event_type)
            print "time: " + str(popped.time)
            print "flow: " + str(popped.flow.src.id)
            if popped.event_type != 'FAST':
                print "packet_id: " + str(popped.packet.id)
                print "packet size : " + str(popped.packet.size)
                print "packet type : " + str(popped.packet.type)
                print "current link end 1: " + str(popped.link.end_1.id)
                print "current link end 2: " + str(popped.link.end_2.id)
                print "source: " + str(popped.packet.source.id)
                print "destination: " + str(popped.packet.destination.id)
                print "route: " + str(popped.packet.route)
            print "\n"
        
        return popped 
    
    #if the queue is empty then return 1, otherwise return 0
    def is_empty(self):
        if self.queue_size == 0:
            return 1
