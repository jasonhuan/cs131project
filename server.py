#!/usr/bin/python

import sys
import asyncio
import time
import aiohttp
import json
import re
import logging

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
			logging.info("received: %s", split)

			if(len(split) == 0):
				err = "?"
				writer.write(err.encode())
				return
				
			if(split[0] == "AT"):
				if(len(split) != 6):
					err = "? " + decoded
					writer.write(err.encode())
					return

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
				if(len(split) != 4):
					err = "? " + decoded
					writer.write(err.encode())
					return


				separate = re.split('[-+]', split[2][1:])
				if len(separate) != 2:
					logging.info("invalid coordinates")
					return

				if split[2][0] == '+':
					latitude = float(separate[0])
				elif split[2][0] == '-':
					latitude = -1 * float(separate[0])
				else:
					logging.info("invalid first character in coordinates")
					return

				if '-' in split[2][1:]:
					longitude = -1 * float(separate[1])
				else:
					longitude = float(separate[1])

				if not (-90 < latitude < 90 and -180 < longitude < 180):
					logging.info("latitude or longitude values out of bounds")
					return


				current = time.time()
				diff = current - float(split[3])

				if(diff > 0):
					diff = float('+' + str(diff))
				
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
						logging.info("no data inserted")
						pass
				except KeyError:
					pips[client] = data
					newValue = True

				logging.info("response: %s", response)

				if(newValue == True):
					#		AT Hill timeDiff clientID coords timestamp
					flood = 'AT {} {} {} {} {}'.format(response[1], response[2], response[3], response[4], response[5])
					await flooding_algorithm(flood)


			elif(split[0] == 'WHATSAT'):
				if(len(split) != 4):
					err = "? " + decoded
					writer.write(err.encode())
					return

				client = split[1]
				radius = split[2]
				items = split[3]
				try:
					int(radius)
					int(items)
				except:
					err = "? " + decoded
					writer.write(err.encode())
					return

				if(int(radius) > 50 or int(radius) < 0 or int(items) > 20 or int(items) < 0):
					err = "? " + decoded
					writer.write(err.encode())
					return

				try:
					lookup = pips[client]
					response = 'AT {} {} {} {} {}'.format(lookup[0], lookup[1], lookup[2], lookup[3], lookup[4])
					
					storedCoordinates = lookup[3]
					placesQuery = await findPlaces(storedCoordinates, int(radius), items)

					finalResponse = response + '\n' + str(placesQuery) +'\n' + '\n'

					writer.write(finalResponse.encode())

				except KeyError:
					logging.info("cannot find data for client: %s", split[1])
					writer.write(b'no data')
			
			else:
				err = "? " + decoded
				logging.info(err)
				writer.write(err.encode())
				return

			await writer.drain()

async def findPlaces(coordinates, radius, maxItems):
	separate = re.split('[+-]', coordinates[1:])

	lat = float(separate[0])
	lng = float(separate[1])

	lat_sign = (1 if coordinates[0] == '+' else -1)
	lng_sign = (1 if ('+' in coordinates[1:]) else -1)

	lat, lng = lat * lat_sign, lng * lng_sign

	url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&key={APIKEY}".format(lat = lat, lng = lng, radius = radius * 1000, APIKEY = APIKEY)
	logging.info("findPlaces URL: %s", url)
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			#print("Status:", response.status)
			#print("Content-type:", response.headers['content-type'])

			html = await response.text()
			#print("Body:", html)

			body_obj = json.loads(html)
			if len(body_obj["results"]) <= float(maxItems):
				return html
			else:
				body_obj["results"] = body_obj["results"][:int(maxItems)]
				return json.dumps(body_obj, sort_keys=True, indent=4)

async def flooding_algorithm(data):
	if(sys.argv[1] == 'Hill'):
		try:
			jaquezReader, jaquezWriter = await asyncio.open_connection(port=11536)
			logging.info('Send: %s to Jaquez', data)
			jaquezWriter.write(str(data).encode())
		except IOError as e:
			logging.info("unable to connect to Jaquez")
			pass

		try:
			smithReader, smithWriter = await asyncio.open_connection(port=11537)
			logging.info('Send: %s to Smith', data)
			smithWriter.write(str(data).encode())
		except IOError as e:
			logging.info("unable to connect to Smith")
			pass

	if(sys.argv[1] == 'Jaquez'):
		try:
			hillReader, hillWriter = await asyncio.open_connection(port=11535)
			logging.info('Send: %s to Hill', data)
			hillWriter.write(str(data).encode())
		except IOError as e:
			logging.info("unable to connect to Hill")
			pass

		try:
			singletonReader, singletonWriter = await asyncio.open_connection(port=11538)
			logging.info('Send: %s to Singleton', data)
			singletonWriter.write(str(data).encode())
		except IOError as e:
			logging.info("unable to connect to Singleton")
			pass

	if(sys.argv[1] == 'Smith'):
		try:
			hillReader, hillWriter = await asyncio.open_connection(port=11535)
			logging.info('Send: %s to Hill', data)
			hillWriter.write(str(data).encode())
		except IOError as e:
			logging.info("unable to connect to Hill")
			pass

		try:
			singletonReader, singletonWriter = await asyncio.open_connection(port=11538)
			logging.info('Send: %s to Singleton', data)
			singletonWriter.write(str(data).encode())
		except IOError as e:
			logging.info("unable to connect to Singleton")
			pass

		try:
			campbellReader, campbellWriter = await asyncio.open_connection(port=11539)
			logging.info('Send: %s to Campbell', data)
			campbellWriter.write(str(data).encode())
		except IOError as e:
			logging.info("unable to connect to Campbell")
			pass

	if(sys.argv[1] == 'Singleton'):
		try:
			jaquezReader, jaquezWriter = await asyncio.open_connection(port=11536)
			logging.info('Send: %s to Jaquez', data)
			jaquezWriter.write(str(data).encode())
		except IOError as e:
			logging.info("unable to connect to Jaquez")
			pass

		try:
			smithReader, smithWriter = await asyncio.open_connection(port=11537)
			logging.info('Send: %s to Smith', data)
			smithWriter.write(str(data).encode())
		except IOError as e:
			logging.info("unable to connect to Smith")
			pass

		try:
			campbellReader, campbellWriter = await asyncio.open_connection(port=11539)
			logging.info('Send: %s to Campbell', data)
			campbellWriter.write(str(data).encode())
		except IOError as e:
			logging.info("unable to connect to Campbell")
			pass

	if(sys.argv[1] == 'Campbell'):
		try:
			smithReader, smithWriter = await asyncio.open_connection(port=11537)
			logging.info('Send: %s to Smith', data)
			smithWriter.write(str(data).encode())
		except IOError as e:
			logging.info("unable to connect to Smith")
			pass

		try:
			singletonReader, singletonWriter = await asyncio.open_connection(port=11538)
			logging.info('Send: %s to Singleton', data)
			singletonWriter.write(str(data).encode())
		except IOError as e:
			logging.info("unable to connect to Singleton")
			pass

async def main():
	#print('Number of arguments:', len(sys.argv), 'arguments.')
	#print('Argument List:', str(sys.argv))

	s_name = sys.argv[1]
	logging.basicConfig(filename="server_{}.log".format(s_name), format='%(levelname)s: %(message)s', filemode='w+', level=logging.INFO)

	if(sys.argv[1] == 'Hill'):
		server = await asyncio.start_server(handle_client, port=11535)
		logging.info("server Hill started")

		try:
			jaquezReader, jaquezWriter = await asyncio.open_connection(port=11536)
			logging.info("connected to Jaquez")

		except IOError as e:
			logging.info("unable to connect to Jaquez")
		
		try:
			smithReader, smithWriter = await asyncio.open_connection(port=11537)
			logging.info("connected to Smith")
		except IOError as e:
			logging.info("unable to connect to Smith")

	elif(sys.argv[1] == 'Jaquez'):
		server = await asyncio.start_server(handle_client, port=11536)
		logging.info("server Jaquez started")

		try:
			hillReader, hillWriter = await asyncio.open_connection(port=11535)
			logging.info("connected to Hill")
		except IOError as e:
			logging.info("unable to connect to Hill")

		try:
			singletonReader, singletonWriter = await asyncio.open_connection(port=11538)
			logging.info("connected to Singleton")
		except IOError as e:
			logging.info("unable to connect to Singleton")

	elif(sys.argv[1] == 'Smith'):
		server = await asyncio.start_server(handle_client, port=11537)
		logging.info("server Smith started")

		try:
			hillReader, hillWriter = await asyncio.open_connection(port=11535)
			logging.info("connected to Hill")
		except IOError as e:
			logging.info("unable to connect to Hill")

		try:
			singletonReader, singletonWriter = await asyncio.open_connection(port=11538)
			logging.info("connected to Singleton")
		except IOError as e:
			logging.info("unable to connect to Singleton")

		try:
			campbellReader, campbellWriter = await asyncio.open_connection(port=11539)
			logging.info("connected to Campbell")
		except IOError as e:
			logging.info("unable to connect to Campbell")

	elif(sys.argv[1] == 'Singleton'):
		server = await asyncio.start_server(handle_client, port=11538)
		logging.info("server Singleton started")
		
		try:
			jaquezReader, jaquezWriter = await asyncio.open_connection(port=11536)
			logging.info("connected to Jaquez")
		except IOError as e:
			logging.info("unable to connect to Jaquez")
		
		try:
			smithReader, smithWriter = await asyncio.open_connection(port=11537)
			logging.info("connected to Smith")
		except IOError as e:
			logging.info("unable to connect to Smith")
		
		try:
			campbellReader, campbellWriter = await asyncio.open_connection(port=11539)
			logging.info("connected to Campbell")
		except IOError as e:
			logging.info("unable to connect to Campbell")

	elif(sys.argv[1] == 'Campbell'):
		server = await asyncio.start_server(handle_client, port=11539)
		logging.info("server Campbell started")

		try:
			smithReader, smithWriter = await asyncio.open_connection(port=11537)
			logging.info("connected to Smith")
		except IOError as e:
			logging.info("unable to connect to Smith")

		try:
			singletonReader, singletonWriter = await asyncio.open_connection(port=11538)
			logging.info("connected to Singleton")
		except IOError as e:
			logging.info("unable to connect to Singleton")
	else:
		logging.info("invalid server name")
		return;

	addr = server.sockets[0].getsockname()
	logging.info('Serving on %s', addr)
	
	async with server:
		await server.serve_forever()



if __name__ == "__main__":
    asyncio.run(main())