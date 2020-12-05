#!/usr/bin/python

import sys
import asyncio

async def handle_client(reader, writer):

	while 1:
		data = await reader.read(1024)
		if not data:
			w.close()
			break
		else:
			w.write("server response")
			await w.drain()

async def start_server(name):
	if(name == 'Hill'):
		await asyncio.start_server(handle_client, port=11535)
		print("server started")

async def main(argv):
	print('Number of arguments:', len(sys.argv), 'arguments.')
	print('Argument List:', str(sys.argv))

	await start_server(argv[1])

if __name__ == "__main__":
    asyncio.run(main(sys.argv))
