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
        self.currentIteration = 0
        self.next_sequence_number = 0
        self.last_ACKed = 0
        self.sent_segments = []
        self.timer = 0
        self.timeout = 10

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

        print("getDataReceived(): Complete this...")

        # ############################################################################################################ #
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
        """Implements a stop and wait go back N approach.

        If the last acknowledged number is less than the next sequence number and
        the current iteration exceeds the timeout window, the data that hasn't yet
        been acknowledged will be resent. Otherwise, as long as there is data
        left to send and if fits within the flow control window, it is processed
        into packets of DATA_LENGTH and sent through the unreliable channel."""

        # ############################################################################################################ #
        print(
            f"next_sequence_number: {self.next_sequence_number}, Acked: {self.last_ACKed}"
        )

        # If packets were lost and the timeout window is exceeded, resend the previous segments.
        if self.last_ACKed < self.next_sequence_number:
            if (self.currentIteration - self.timer) >= self.timeout:
                print("timeout resending")

                # sets timer to current iteration, in order to keep track of that iterations time out window.
                self.timer = self.currentIteration

                # Resends previously unacknowledged segments
                for segment in self.sent_segments:
                    self.sendChannel.send(segment)

        # Processes packets as long as there is data to send, and it fits within the flow control window.
        while (self.next_sequence_number < len(self.dataToSend)) and (
            self.next_sequence_number < self.last_ACKed + RDTLayer.FLOW_CONTROL_WIN_SIZE
        ):
            # variable for a new empty packet.
            segment_send = Segment()

            # Variable to hold the sequence number
            seq_num = self.next_sequence_number

            # Variable to hold the data to send starting at .next_sequence_number up to DATA_Length
            data = self.dataToSend[
                self.next_sequence_number : self.next_sequence_number
                + RDTLayer.DATA_LENGTH
            ]

            segment_send.setData(seq_num, data)
            print("Sending segment: ", segment_send.to_string())

            # Sends data through the unreliable channel.
            self.sendChannel.send(segment_send)

            # Appends the sent segments to a list for tracking.
            self.sent_segments.append(segment_send)
            self.next_sequence_number += len(data)

    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):
        segmentAck = Segment()  # Segment acknowledging packet(s) received

        # This call returns a list of incoming segments (see Segment class)...
        listIncomingSegments = self.receiveChannel.receive()

        # ############################################################################################################ #
        # What segments have been received?
        # How will you get them back in order?
        # This is where a majority of your logic will be implemented

        print("processReceive(): Complete this...")

        # ############################################################################################################ #
        # How do you respond to what you have received?
        # How can you tell data segments apart from ack segemnts?
        print("processReceive(): Complete this...")

        # Somewhere in here you will be setting the contents of the ack segments to send.
        # The goal is to employ cumulative ack, just like TCP does...

        # ############################################################################################################ #
        # Display response segment

        print("Sending ack: ", segmentAck.to_string())

        # Use the unreliable sendChannel to send the ack packet
