#!/usr/bin/python

import sys
import asyncio

pips = {}

async def handle_client(reader, writer):

	while 1:
		data = await reader.read(1024)
		if not data:
			#writer.close()
			break
		else:
			decoded = data.decode()
			split = decoded.split()
			#print(split)

			if(len(split) != 4):
				err = "? " + decoded
				writer.write(err.encode())
				return

			if(split[0] == 'IAMAT'):
				coordinates = split[2]
				time = split[3]
				pips[split[1]] = (coordinates, time)

				writer.write(b'message received')
				#<Implement flooding algorithm to other servers>
				print(split[1], ":", pips[split[1]])

			elif(split[0] == 'WHATSAT'):
				client = split[1]
				radius = split[2]
				items = split[3]
				if(int(radius) > 50 or int(items) > 20):
					err = "? " + decoded
					writer.write(err.encode())
					return
				try:
					lookup = pips[split[1]]
					writer.write(str(lookup).encode())
				except KeyError:
					writer.write(b'no data')
				
				#<API call to Google Places>

			
			await writer.drain()


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