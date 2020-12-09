#!/usr/bin/python

import sys
import asyncio
import time
import aiohttp
import json

pips = {}
APIKEY = "AIzaSyAULO58fqkF4UBJCVq_bJylG1zlrdErvzg"

async def handle_client(reader, writer):

	while 1:
		data = await reader.read(1024)
		if not data:
			#writer.close()
			break
		else:
			decoded = data.decode()
			split = decoded.split()
			print("received:", split)


			if(split[0] == "AT"):
				print("AT received")
				try:
					storedTimestamp = pips[split[3]][4]
					if(storedTimestamp != split[5]): #if the current timestamp inside of pips[] does not match the incoming timestamp for the client ID
						pips[split[3]] = split[1:]
						flood = 'AT {} {} {} {} {}'.format(split[1], split[2], split[3], split[4], split[5])
						await flooding_algorithm(flood)
					else:
						pass
				except KeyError:
					pips[split[3]] = split[1:]

					flood = 'AT {} {} {} {} {}'.format(split[1], split[2], split[3], split[4], split[5])
					await flooding_algorithm(flood)

			elif(split[0] == 'IAMAT'):
				current = time.time()
				diff = current - float(split[3])

				
				response = split[1:]
				response.insert(0, diff)
				response.insert(0, sys.argv[1])
				response.insert(0, 'AT')

				writer.write(str(response).encode())

				client = response[3]
				data = response[1:]

				newValue = False

				try:
					existingTimestamp = pips[client][4]
					if(existingTimestamp != split[3]):
						newValue = True
						pips[client] = data
					else:
						print("no data inserted")
						pass
				except KeyError:
					pips[client] = data
					newValue = True

				print("response:", response)

				if(newValue == True):
					#		AT Hill timeDiff clientID coords timestamp
					flood = 'AT {} {} {} {} {}'.format(response[1], response[2], response[3], response[4], response[5])
					await flooding_algorithm(flood)


			elif(split[0] == 'WHATSAT'):
				client = split[1]
				radius = split[2]
				print("radius:", radius)
				items = split[3]
				if(int(radius) > 50 or int(radius) < 0 or int(items) > 20 or int(items) < 0):
					err = "? " + decoded
					writer.write(err.encode())
					return

				try:
					lookup = pips[client]
					
					writer.write(str(lookup).encode())
					try:
						placesQuery = await findPlaces("34.068930", "-118.445127", int(radius), items)
					except:
						print("error occured with findPlaces()")

				except KeyError:
					print("cannot find data for client:", split[1])
					writer.write(b'no data')
			
			else:
				err = "? " + decoded
				print(err)
				writer.write(err.encode())
				return

			await writer.drain()

async def findPlaces(lat, lng, radius, maxItems):
	url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&key={APIKEY}".format(lat = lat, lng = lng, radius = radius * 1000, APIKEY = APIKEY)
	print("findPlaces URL", url)
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			print("Status:", response.status)
			print("Content-type:", response.headers['content-type'])

			html = await response.text()
			print("Body:", html)


	return response

async def flooding_algorithm(data):
	if(sys.argv[1] == 'Hill'):
		try:
			jaquezReader, jaquezWriter = await asyncio.open_connection(port=11536)
			print(f'Send: {data!r} to Jaquez')
			jaquezWriter.write(str(data).encode())
		except IOError as e:
			print("unable to connect to Jaquez")

		try:
			smithReader, smithWriter = await asyncio.open_connection(port=11537)
			print(f'Send: {data!r} to Smith')
			smithWriter.write(str(data).encode())
		except IOError as e:
			print("unable to connect to Smith")

	if(sys.argv[1] == 'Jaquez'):
		try:
			hillReader, hillWriter = await asyncio.open_connection(port=11535)
			print(f'Send: {data!r} to Hill')
			hillWriter.write(str(data).encode())
		except IOError as e:
			print("unable to connect to Hill")

		try:
			singletonReader, singletonWriter = await asyncio.open_connection(port=11538)
			print(f'Send: {data!r} to Singleton')
			singletonWriter.write(str(data).encode())
		except IOError as e:
			print("unable to connect to Singleton")

	if(sys.argv[1] == 'Smith'):
		try:
			hillReader, hillWriter = await asyncio.open_connection(port=11535)
			print(f'Send: {data!r} to Hill')
			hillWriter.write(str(data).encode())
		except IOError as e:
			print("unable to connect to Hill")

		try:
			singletonReader, singletonWriter = await asyncio.open_connection(port=11538)
			print(f'Send: {data!r} to Singleton')
			singletonWriter.write(str(data).encode())
		except IOError as e:
			print("unable to connect to Singleton")

		try:
			campbellReader, campbellWriter = await asyncio.open_connection(port=11539)
			print(f'Send: {data!r} to Campbell')
			campbellWriter.write(str(data).encode())
		except IOError as e:
			print("unable to connect to Campbell")

	if(sys.argv[1] == 'Singleton'):
		try:
			jaquezReader, jaquezWriter = await asyncio.open_connection(port=11536)
			print(f'Send: {data!r} to Jaquez')
			jaquezWriter.write(str(data).encode())
		except IOError as e:
			print("unable to connect to Jaquez")

		try:
			smithReader, smithWriter = await asyncio.open_connection(port=11537)
			print(f'Send: {data!r} to Smith')
			smithWriter.write(str(data).encode())
		except IOError as e:
			print("unable to connect to Smith")

		try:
			campbellReader, campbellWriter = await asyncio.open_connection(port=11539)
			print(f'Send: {data!r} to Campbell')
			campbellWriter.write(str(data).encode())
		except IOError as e:
			print("unable to connect to Campbell")

	if(sys.argv[1] == 'Campbell'):
		try:
			smithReader, smithWriter = await asyncio.open_connection(port=11537)
			print(f'Send: {data!r} to Smith')
			smithWriter.write(str(data).encode())
		except IOError as e:
			print("unable to connect to Smith")

		try:
			singletonReader, singletonWriter = await asyncio.open_connection(port=11538)
			print(f'Send: {data!r} to Singleton')
			singletonWriter.write(str(data).encode())
		except IOError as e:
			print("unable to connect to Singleton")

async def main():
	print('Number of arguments:', len(sys.argv), 'arguments.')
	print('Argument List:', str(sys.argv))

	if(sys.argv[1] == 'Hill'):
		server = await asyncio.start_server(handle_client, port=11535)
		print("server Hill started")

		try:
			jaquezReader, jaquezWriter = await asyncio.open_connection(port=11536)
			print("connected to Jaquez")

		except IOError as e:
			print("unable to connect to Jaquez")
		
		try:
			smithReader, smithWriter = await asyncio.open_connection(port=11537)
			print("connected to Smith")
		except IOError as e:
			print("unable to connect to Smith")

	elif(sys.argv[1] == 'Jaquez'):
		server = await asyncio.start_server(handle_client, port=11536)
		print("server Jaquez started")

		try:
			hillReader, hillWriter = await asyncio.open_connection(port=11535)
			print("connected to Hill")
		except IOError as e:
			print("unable to connect to Hill")

		try:
			singletonReader, singletonWriter = await asyncio.open_connection(port=11538)
			print("connected to Singleton")
		except IOError as e:
			print("unable to connect to Singleton")

	elif(sys.argv[1] == 'Smith'):
		server = await asyncio.start_server(handle_client, port=11537)
		print("server Smith started")

		try:
			hillReader, hillWriter = await asyncio.open_connection(port=11535)
			print("connected to Hill")
		except IOError as e:
			print("unable to connect to Hill")

		try:
			singletonReader, singletonWriter = await asyncio.open_connection(port=11538)
			print("connected to Singleton")
		except IOError as e:
			print("unable to connect to Singleton")

		try:
			campbellReader, campbellWriter = await asyncio.open_connection(port=11539)
			print("connected to Campbell")
		except IOError as e:
			print("unable to connect to Campbell")

	elif(sys.argv[1] == 'Singleton'):
		server = await asyncio.start_server(handle_client, port=11538)
		print("server Singleton started")
		
		try:
			jaquezReader, jaquezWriter = await asyncio.open_connection(port=11536)
			print("connected to Jaquez")
		except IOError as e:
			print("unable to connect to Jaquez")
		
		try:
			smithReader, smithWriter = await asyncio.open_connection(port=11537)
			print("connected to Smith")
		except IOError as e:
			print("unable to connect to Smith")
		
		try:
			campbellReader, campbellWriter = await asyncio.open_connection(port=11539)
			print("connected to Campbell")
		except IOError as e:
			print("unable to connect to Campbell")

	elif(sys.argv[1] == 'Campbell'):
		server = await asyncio.start_server(handle_client, port=11539)
		print("server Campbell started")

		try:
			smithReader, smithWriter = await asyncio.open_connection(port=11537)
			print("connected to Smith")
		except IOError as e:
			print("unable to connect to Smith")

		try:
			singletonReader, singletonWriter = await asyncio.open_connection(port=11538)
			print("connected to Singleton")
		except IOError as e:
			print("unable to connect to Singleton")
		

	addr = server.sockets[0].getsockname()
	print(f'Serving on {addr}')
	
	async with server:
		await server.serve_forever()



if __name__ == "__main__":
    asyncio.run(main())