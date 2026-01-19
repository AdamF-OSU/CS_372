from socket import *
serverName = 'gaia.cs.umass.edu'
serverPort = 80
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
request = "GET /wireshark-labs/INTRO-wireshark-file1.html HTTP/1.1\r\nHost:gaia.cs.umass.edu\r\n\r\n"
clientSocket.send(request.encode())
contentReceived = clientSocket.recv(1024)

print(f"\nRequest: {request}")
print(f"Length-Recieved: {len(contentReceived)}")
print(contentReceived.decode())
clientSocket.close()