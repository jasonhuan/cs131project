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
			print(split)

			if(len(split) != 5):
				err = "? " + decoded
				writer.write(err.encode())
				return
			if(split[0] == 'IAMAT'):
				latitude = split[2]
				longitude = split[3]
				time = split[4]
			#elif(data.decode[0] == 'WHATSAT'):
			
			pips[split[1]] = (latitude, longitude, time)
			print(split[1], ":", pips[split[1]])
			await writer.drain()


async def main():
	print('Number of arguments:', len(sys.argv), 'arguments.')
	print('Argument List:', str(sys.argv))

	if(sys.argv[1] == 'Hill'):
		server = await asyncio.start_server(handle_client, port=11535)
		print("server Hill started")
	elif(sys.argv[1] == 'Jaquez'):
		server = await asyncio.start_server(handle_client, port=11536)
		print("server Jaquez started")
	elif(sys.argv[1] == 'Smith'):
		server = await asyncio.start_server(handle_client, port=11537)
		print("server Smith started")
	elif(sys.argv[1] == 'Singleton'):
		server = await asyncio.start_server(handle_client, port=11538)
		print("server Singleton started")
	elif(sys.argv[1] == 'Campbell'):
		server = await asyncio.start_server(handle_client, port=11539)
		print("server Campbell started")

	addr = server.sockets[0].getsockname()
	print(f'Serving on {addr}')

	
	async with server:
		await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())