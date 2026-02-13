from segment import Segment


# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
#                                                                                                                      #
#                                                                                                                      #
# Notes:                                                                                                               #
# This file is meant to be changed.                                                                                    #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    DATA_LENGTH = 4  # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = (
        15  # in characters          # Receive window size for flow-control
    )
    sendChannel = None
    receiveChannel = None
    dataToSend = ""
    currentIteration = 0  # Use this for segment 'timeouts'
    # Add items as needed

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ""
        self.dataReceived = ""
        self.currentIteration = 0
        self.next_sequence_number = 0
        self.last_ACKed = 0
        self.sent_segments = []             # Keeps track of sent segments, used to implement go back N
        self.timer = 0                      # Define a timer.
        self.timeout = 10                   # Set timeout window
        self.expected_sequence_number = 0
        self.countSegmentTimeouts = 0

        # Add items as needed

    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################ #
    # setDataToSend()                                                                                                  #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the string data to send                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setDataToSend(self, data):
        self.dataToSend = data

    # ################################################################################################################ #
    # getDataReceived()                                                                                                #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to get the currently received and buffered string data, in order                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def getDataReceived(self):
        # ############################################################################################################ #
        # Identify the data that has been received...

        print(f"getDataReceived(): {self.dataReceived}")

        #
        # ############################################################################################################ #+
        return self.dataReceived

    # ################################################################################################################ #
    # processData()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # "timeslice". Called by main once per iteration                                                                   #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    # ################################################################################################################ #
    # processSend()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment sending tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processSend(self):
        """Implements a stop and wait, go back N approach.

        If the last acknowledged number is less than the next sequence number and
        the current iteration exceeds the timeout window, the data that hasn't yet
        been acknowledged will be resent. Otherwise, as long as there is data
        left to send and if fits within the flow control window, it is processed
        into packets of DATA_LENGTH and sent through the unreliable channel.

        Sources used: Computer Networking: a Top-Down Approach (9th ed.)
                      J.F. Kurose, K.W. Ross, Pearson, 2026
                      http://gaia.cs.umass.edu/kurose_ross"""

        # ############################################################################################################ #

        print(f"next_sequence_number: {self.next_sequence_number}, Acked: {self.last_ACKed}")

        # If last acked < the next sequence number packets were lost.
        if self.last_ACKed < self.next_sequence_number:

            # (Current iteration - timer) keeps track of the current iterations time.
            # If it exceeds the timeout window, it resends segments.
            if (self.currentIteration - self.timer) >= self.timeout:

                print("timeout resending")

                # Resends previously unacknowledged segments
                for segment in self.sent_segments:
                    self.sendChannel.send(segment)

                self.timer = self.currentIteration       # Reset timer.
                self.countSegmentTimeouts += 1           # Implemented suggestion from https://edstem.org/us/courses/90274/discussion/7635500



        # Processes packets as long as there is data to send, and it fits within the flow control window.
        while (self.next_sequence_number < len(self.dataToSend)) and (
            self.next_sequence_number < self.last_ACKed + RDTLayer.FLOW_CONTROL_WIN_SIZE
        ):

            segmentSend = Segment()                     # Create a new empty packet.
            seqnum = self.next_sequence_number          # Variable to hold sequence number


            data = self.dataToSend[seqnum : seqnum + RDTLayer.DATA_LENGTH]  # Defines the data to send, uses slicing to create a chunk of DATA_LENGTH.
            segmentSend.setData(seqnum, data)                               # Uses setData to create the checksum.

            print("Sending segment: ", segmentSend.to_string())


            self.sendChannel.send(segmentSend)          # Sends data through the unreliable channel.
            self.sent_segments.append(segmentSend)      # Appends the sent segments to a list for tracking.
            self.next_sequence_number += len(data)      # Sets sequence number for the next segment.


    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):


        # This call returns a list of incoming segments (see Segment class)...
        listIncomingSegments = self.receiveChannel.receive()

        # Iterate through the incoming segments.
        for packet in listIncomingSegments:
            if packet.acknum == -1:                 # If the packet contains data.

                # If the checksum fails, send ack for the expected_sequence_number for that packet to be resent.
                if not packet.checkChecksum():
                    segmentAck = Segment()
                    segmentAck.setAck(self.expected_sequence_number)
                    self.sendChannel.send(segmentAck)

                # If the packet is out of order, send ack for the expected_sequence_number for that packet to be resent.
                # This should account for dropped packets as well.
                elif packet.seqnum != self.expected_sequence_number:
                    segmentAck = Segment()
                    segmentAck.setAck(self.expected_sequence_number)
                    self.sendChannel.send(segmentAck)

                # Else append the packets data to dataReceived and increment the next expect sequence number.
                else:
                    self.dataReceived += packet.payload
                    self.expected_sequence_number += len(packet.payload)

                    segmentAck = Segment()
                    segmentAck.setAck(self.expected_sequence_number)
                    self.sendChannel.send(segmentAck)



        # ############################################################################################################ #
        # What segments have been received?
        # How will you get them back in order?
        # This is where a majority of your logic will be implemented

        print(f"processReceive():{self.dataReceived}")

        # ############################################################################################################ #
        # How do you respond to what you have received?
        # How can you tell data segments apart from ack segemnts?
        print("processReceive(): Complete this...")

        # Somewhere in here you will be setting the contents of the ack segments to send.
        # The goal is to employ cumulative ack, just like TCP does...

        # ############################################################################################################ #
        # Display response segment

        print("Sending ack: ", )

        # Use the unreliable sendChannel to send the ack packet
