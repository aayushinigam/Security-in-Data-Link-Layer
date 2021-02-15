import socket
import sys
import pickle
import threading
import numpy as np
PORT = 12345
KEY = '1001'
SPACE_CODE = 91

CIPHER_INV = np.array([
    [1, 0, 1],
    [4, 4, 3],
    [-4, -3, -3]
])


def calculateXOR(b1,b2) :
	temp_xor = int(b1,2) ^ int(b2,2)
	#xor_string = "{0:b}".format(temp_xor)
	xor_string = format(temp_xor,'03b')
	return xor_string


def calculateRemainder(binary_data):
	n1 = len(KEY)
	n2 = len(binary_data)
	temp_data = binary_data[:n1]
	for i in range(n1,n2) :
		if temp_data[0] == '1':
			xor = calculateXOR(KEY,temp_data)
			temp_data = xor + binary_data[i]
		else:       	
			xor = calculateXOR('0' * i,temp_data) 
			temp_data = xor + binary_data[i]
	if temp_data[0] == '1':
		temp_data = calculateXOR(KEY,temp_data)
	else:
		temp_data = calculateXOR('0'*i, temp_data)
	return temp_data

    
def calculateCRC(data) :
	#convert input string to binary string
	binary_data = (''.join(format(ord(x), 'b') for x in data))
	#padding with zeroes
	binary_data = binary_data + '0' * (len(KEY)-1) 
	return calculateRemainder(binary_data)


def decodeMsg(decrypted_array) :
	msg = ''
	for i in decrypted_array :
		char = 64 + i
		if(char == SPACE_CODE) :
			msg += ' '
		else :
			msg += chr(char)
	return (msg)


def decryptData(encrypted_matrix) :
	decrypted_matrix = np.dot(CIPHER_INV,encrypted_matrix)
	decrypted_array = decrypted_matrix.flatten('F')
	return(decodeMsg(decrypted_array))


def newClient(client_sock,addr) :
 
	while True : 
		#receive msg
		data1 = client_sock.recv(1024)
		encrypted_data = pickle.loads(data1)
		#receive crc
		data2 = client_sock.recv(1024)
		sender_crc = pickle.loads(data2)
		#decrypt the msg
		msg = decryptData(encrypted_data)
		reciever_crc = calculateCRC(msg.strip())
		print("Message received is : ", msg)
		if(sender_crc == reciever_crc) :
			print("No error in the received msg")
		else :
			print("Error in the received msg")



#main() CODE 
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((socket.gethostname(), PORT))
server_sock.listen()
while True :
	try :
		client, addr = server_sock.accept()
		#new thread for every client
		threading._start_new_thread(newClient,(client,addr))
	except KeyboardInterrupt as e :
		print("\nserver shutting down")
		server_sock.close()
		sys.exit(0)