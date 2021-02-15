import socket 
import numpy as np
import pickle 
import sys

#global constants
PORT = 12345
SPACE_CODE = 27
KEY = '1001'

CIPHER = np.array([
    [-3, -3, -4],
    [0, 1, 1],
    [4, 3, 4]
])
 
def calculateXOR(b1,b2) :
	temp_xor = int(b1,2) ^ int(b2,2)
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
	

def convertArrayToMatrix(vectors) :
	matrix = np.array(vectors)
	matrix = matrix.reshape(3,-1,order='F')
	return matrix



def encodeData(inp) :
	vectors = []
	for i in inp :
		temp = ord(i) - 64
		if(temp > 0) :
			vectors.append(temp)
		else :
			vectors.append(SPACE_CODE)

	#make it into a multiple of 3
	while True :
		if(len(vectors) % 3 == 0) :
			break
		vectors.append(SPACE_CODE)
	return(convertArrayToMatrix(vectors))


def encryptData(matrix) :
	return np.dot(CIPHER,matrix)



#MAIN STARTS HERE : 
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((socket.gethostname(), PORT))
 
while True : 
	try :
		inp = input("Enter data : ")
		data_matrix = encodeData(inp)
		crc = calculateCRC(inp.strip())
		encrypted_data = encryptData(data_matrix)

		encrypted_data = pickle.dumps(encrypted_data)
		crc = pickle.dumps(crc)

		client_sock.send(encrypted_data)
		print("sent msg")
		client_sock.send(crc)
	except KeyboardInterrupt as e :
		print("\nshutting down client ")
		client_sock.close()
		sys.exit(0) 

