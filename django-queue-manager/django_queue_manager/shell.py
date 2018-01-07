import socket
import sys

def send_data():
	'''Used to connect and get/manage the status of the socket'''
	socket_host = str(sys.argv[1])
	socket_port = int(sys.argv[2])
	data = str(sys.argv[3]).encode()
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((socket_host, socket_port))
	sock.send(data)
	received = sock.recv(1024)
	sock.close()
	print("Sent: {0}".format(data))
	print("Received: {0}".format(received))


if __name__ == "__main__":
	send_data()

