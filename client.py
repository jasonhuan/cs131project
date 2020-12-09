#!/usr/bin/python

import sys
import asyncio


async def main():
	#print('Number of arguments:', len(sys.argv), 'arguments.')
	#print('Argument List:', str(sys.argv))

	if(sys.argv[1] == 'Hill'):
		reader, writer = await asyncio.open_connection(port=11535)
	elif(sys.argv[1] == 'Jaquez'):
		reader, writer = await asyncio.open_connection(port=11536)
	elif(sys.argv[1] == 'Smith'):
		reader, writer = await asyncio.open_connection(port=11537)
	elif(sys.argv[1] == 'Singleton'):
		reader, writer = await asyncio.open_connection(port=11538)
	elif(sys.argv[1] == 'Campbell'):
		reader, writer = await asyncio.open_connection(port=11539)
	else:
		print("Unrecognized server")
		return

	message = ''
	for x in range(2, len(sys.argv)):
		if(x != 2):
			message += ' '
		message += sys.argv[x]

	#print(f'Send: {message!r}')
	writer.write(message.encode())

	data = await reader.read(20000)
	decoded = data.decode()
	print(decoded)

	#print('Close the connection')
	writer.close()

	return

if __name__ == "__main__":
    asyncio.run(main())