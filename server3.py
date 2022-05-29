#Author: Sunil Lal

#This is a simple HTTP server which listens on port 8080, accepts connection request, and processes the client request
#in sepearte threads. It implements basic service functions (methods) which generate HTTP response to service the HTTP requests.
#Currently there are 3 service functions; default, welcome and getFile. The process function maps the requet URL pattern to the service function.
#When the requested resource in the URL is empty, the default function is called which currently invokes the welcome function.
#The welcome service function responds with a simple HTTP response: "Welcome to my homepage".
#The getFile service function fetches the requested html or img file and generates an HTTP response containing the file contents and appropriate headers.

#To extend this server's functionality, define your service function(s), and map it to suitable URL pattern in the process function.

#This web server runs on python v3
#Usage: execute this program, open your browser (preferably chrome) and type http://servername:8080
#e.g. if server.py and broswer are running on the same machine, then use http://localhost:8080
from socket import *
import _thread

serverSocket = socket(AF_INET, SOCK_STREAM)

serverPort = 8080
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(("", serverPort))

serverSocket.listen(5)
print('The server is running')

# Server should be up and running and listening to the incoming connections

#Extract the given header value from the HTTP request message
def getHeader(message, header):
	if message.find(header) > -1:
		value = message.split(header)[1].split()[0]
	else:
		value = None

	return value

#service function to fetch the requested file, and send the contents back to the client in a HTTP response.
def getFile(filename):
	try:
		# open and read the file contents. This becomes the body of the HTTP response
		f = open(filename, "rb")

		body = f.read()
		header = ("HTTP/1.1 200 OK\r\n\r\n").encode()

	except IOError:
		# Send HTTP response message for resource not found
		header = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
		body = "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode()

	return header, body

#service function to generate HTTP response with a simple welcome message
def welcome(message):
	header = "HTTP/1.1 200 OK\r\n\r\n".encode()
	body = ("<html><head></head><body><h1>Welcome to my homepage</h1></body></html>\r\n").encode()

	return header, body

#default service function
def default(message):
	header, body = welcome(message)
	return header, body

#function for sending portfolio.html through http
def portfolio(message):
	with open("portfolio.html", 'r') as f:
		chart = f.read()

	header = "HTTP/1.1 200 OK\r\n\r\n".encode()
	body = chart.encode()

	return header,body

#Function for updating the portfolio
def pUpdate(message):
	#Seperate data returned from html form - symbol, quantity, price
	header = message.split("\r\n")
	body = (header[-1].split("&"))
	x = []
	for i in body:
		x.append(i.split("="))

	nSymbol = x[0][1].upper()
	nQuantity = x[1][1]
	nPrice = x[2][1]

	#Get each stock from xml into list
	import xml.dom.minidom as minidom
	parsed = minidom.parse("portfolio.xml")
	stocks = parsed.getElementsByTagName("Stock")

	#list for if a stock is already in the table
	previousStocks = []

	for i in stocks:
		#Get stock symbol of each stock in the table, record it in previousStocks
		symbol = i.childNodes[0].childNodes[0].data
		previousStocks.append(symbol)
		#If new stock is in the list, update the quantity and price with the new data
		if nSymbol == symbol:
			quantity = i.childNodes[1].childNodes[0].data
			price = i.childNodes[2].childNodes[0].data

			#Add or subtract new amount
			if float(nQuantity) > 0:
				price = (float(quantity)*float(price) + float(nQuantity)*float(nPrice))/(float(quantity) + float(nQuantity))
			quantity = float(quantity) + float(nQuantity)

			#If quantity or price would be changed to below zero, send to error page instead
			if float(quantity) < 0 or float(price) < 0:
				#Make sure quantity and price stay positive
				header = "HTTP/1.1 200 OK\r\n\r\n".encode()
				body = "Quantity and Price cannot be below zero, to remove a stock make the quantity equal zero".encode()
				return header, body
			elif quantity == 0:
				#Remove stock if quantity = 0
				parent = i.parentNode
				parent.removeChild(i)
			else:
				#Update quantity and price with added or subtracted new amount
				i.childNodes[1].childNodes[0].data = quantity
				i.childNodes[2].childNodes[0].data = price

			#Replace xml file with new data as xml
			with open("portfolio.xml", "w") as xml_file:
				parsed.writexml(xml_file)

	#If not in table, Add to end
	import xml.etree.ElementTree as ET
	if nSymbol not in previousStocks:
		#Interpret xml file as element tree, and go to root
		tree = ET.parse("portfolio.xml")
		root = tree.getroot()

		#Create new elements to be added to the end of the 'Stocks' section of the tree
		treeStocks = root.find("Stocks")
		newStock = ET.SubElement(treeStocks, "Stock")
		newName = ET.SubElement(newStock, "Name")
		newQuantity = ET.SubElement(newStock, "Quantity")
		newPrice = ET.SubElement(newStock, "Price")

		#Set attributes as the inputs from the html form
		newName.text = nSymbol
		newQuantity.text = nQuantity
		newPrice.text = nPrice

		#Convert element tree to string
		final = ET.tostring(root)
		final = str(final)

		#Remove speech marks from string
		final = final[2:]
		final = final[:-1]

		#Write string to xml file
		file = open("portfolio.xml", "w")
		file.write(final)
		file.close()

	#After page updates, redirect back to portfolio page, and send portfolio.html through http
	with open("portfolio.html", 'r') as f:
		chart = f.read()
	header = "HTTP/1.1 301 Moved Permanently\r\nLocation: http://localhost:8080/portfolio\r\n\r\n".encode()
	body = chart.encode()

	return header, body

#Function for sending 'research.html' through http
def research(message):
	with open("research.html", 'r') as x:
		research = x.read()

	header = "HTTP/1.1 200 OK\r\n\r\n".encode()
	body = research.encode()

	return header, body



#We process client request here. The requested resource in the URL is mapped to a service function which generates the HTTP reponse
#that is eventually returned to the client.
def process(connectionSocket) :
	# Receives the request message from the client
	message = connectionSocket.recv(1024).decode()
	if len(message) > 1:

		# Extract the path of the requested object from the message
		# Because the extracted path of the HTTP request includes
		# a character '/', we read the path from the second character
		resource = message.split()[1][1:]

		#Authorization
		list = message.split('\r\n')
		y = ""
		for i in list:
			#Find authorization header, and separate the credentials code
			if "Authorization" in i:
				userpass = i
				x = userpass.split()
				y = x[2]
		#Match authentication with expected code
		if y == "MTkwMzI2NzA6MTkwMzI2NzA=" or y== '':
			#Once authorized, get headers and body for relevant page
			if resource == "":
				responseHeader,responseBody = welcome(message)
			elif resource == "portfolio":
				responseHeader,responseBody = portfolio(message)
			elif resource == "portfolio/update":
				responseHeader, responseBody = pUpdate(message)
			elif resource == "research":
				responseHeader, responseBody = research(message)
			else:
				responseHeader,responseBody = getFile(resource)
		else:
			responseHeader = "HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm='portfolio'\r\n\r\n".encode()
			responseBody = "".encode()


	# Send the HTTP response header line to the connection socket
	connectionSocket.send(responseHeader)
	# Send the content of the HTTP body (e.g. requested file) to the connection socket
	connectionSocket.send(responseBody)
	# Close the client connection socket
	connectionSocket.close()


#Main web server loop. It simply accepts TCP connections, and get the request processed in seperate threads.
while True:
	# Set up a new connection from the client
	connectionSocket, addr = serverSocket.accept()
	#Clients timeout after 60 seconds of inactivity and must reconnect.
	connectionSocket.settimeout(60)
	# start new thread to handle incoming request
	_thread.start_new_thread(process,(connectionSocket,))
