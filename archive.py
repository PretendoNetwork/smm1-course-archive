'''
Jonathan Barrow 2021

This will rip courses from SMM1 using NEX to automate the process
Use at your own risk, I am not resposible for any bans

Requires Python 3 and https://github.com/Kinnay/NintendoClients
'''

from nintendo.nex import backend, ranking, datastore_smm, settings, rmc, common, streams
from nintendo.games import SMM
from nintendo import nnas
from anynet import http
import anyio
import time
import sys
import os
import json
import base64

import logging
logging.basicConfig(level=logging.INFO)

json_file = open('config.json')
config = json.load(json_file)

# Unique device info
DEVICE_ID = config['DEVICE_ID']
SERIAL_NUMBER = config['SERIAL_NUMBER']
SYSTEM_VERSION = config['SYSTEM_VERSION']
REGION_ID = config['REGION_ID']
COUNTRY_NAME = config['COUNTRY_NAME']
LANGUAGE = config['LANGUAGE']

USERNAME = config['USERNAME'] #Nintendo network id
PASSWORD = config['PASSWORD'] #Nintendo network password

# Globals (get set later)
nex_token = None
datastore_smm_client = None

# some of these are invalid, I didnt feel like making a list of them all
# this should work just fine though
event_course_ids = range(930000, 930050)
official_maker_course_ids = range(910000, 920001)

async def main():
	os.makedirs('./courses', exist_ok=True)

	await nas_login() # login with NNID
	await backend_setup() # setup the backend NEX client and start scraping

async def nas_login():
	global nex_token

	nas = nnas.NNASClient()
	nas.set_device(DEVICE_ID, SERIAL_NUMBER, SYSTEM_VERSION)
	nas.set_title(SMM.TITLE_ID_EUR, SMM.LATEST_VERSION)
	nas.set_locale(REGION_ID, COUNTRY_NAME, LANGUAGE)

	access_token = await nas.login(USERNAME, PASSWORD)
	nex_token = await nas.get_nex_token(access_token.token, SMM.GAME_SERVER_ID)

async def backend_setup():
	global datastore_smm_client
	
	s = settings.default()
	s.configure(SMM.ACCESS_KEY, SMM.NEX_VERSION)

	async with backend.connect(s, nex_token.host, nex_token.port) as be:
		async with be.login(str(nex_token.pid), nex_token.password) as client:
			datastore_smm_client = datastore_smm.DataStoreClientSMM(client)

			await scrape() # start ripping courses

async def scrape():
	for course_id in range(sys.maxsize): # data_id is a uint64 so try all possible values
		time.sleep(1) # can be removed, used to not spam Nintendo servers too much
		#course_id = 0x3D91EF8 # testing ID
		print('Trying course ID %d...' % course_id)
		try:
			# Get the course data URL
			param = datastore_smm.DataStorePrepareGetParam()
			param.data_id = course_id
			param.extra_data = []

			result = await datastore_smm_client.prepare_get_object(param)

			headers = {header.key: header.value for header in result.headers}
			course_data_url = result.url

			# Get course metadata

			metadata = {
				'is_event_course': False,
				'is_official_maker_course': False,
				'world_record': {},
				'miis': {
					'creator': {},
					'world_record': {},
					'first_complete': {}
				}
			}

			if course_id in event_course_ids or course_id in official_maker_course_ids:

				param = datastore_smm.DataStoreGetMetaParam()
				param.data_id = course_id
				param.persistence_target = datastore_smm.DataStorePersistenceTarget()
				param.persistence_target.owner_id = 0
				param.persistence_target.persistence_id = 0xFFFF
				param.result_option = 6
				param.access_password = 0

				result = await datastore_smm_client.get_metas_multiple_param([param])

				meta_info = result.infos[0]

				metadata['is_event_course'] = course_id in event_course_ids
				metadata['is_official_maker_course'] = course_id in official_maker_course_ids
			else:
				param = DataStoreGetCustomRankingByDataIdParam()
				param.application_id = 0
				param.data_id_list = [course_id]
				param.result_option = 0x27

				result = await get_custom_ranking_by_data_id(param)

				ranking_result = result.ranking_result[0]
				meta_info = ranking_result.meta_info
				
				metadata['stars'] = ranking_result.score

			metadata['upload_time'] = meta_info.create_time.val # I think?
			metadata['course_name'] = meta_info.name
			metadata['creator_pid'] = meta_info.owner_id
			metadata['user_plays'] = meta_info.ratings[0].info.total_value
			unknown1 = meta_info.ratings[1].info.total_value
			metadata['clears'] = meta_info.ratings[2].info.total_value
			metadata['total_attempts'] = meta_info.ratings[3].info.total_value
			metadata['failures'] = meta_info.ratings[4].info.total_value
			unknown2 = meta_info.ratings[5].info.total_value
			unknown3 = meta_info.ratings[6].info.total_value

			# Get course WR data

			param = DataStoreGetCourseRecordParam()
			param.data_id = course_id
			param.slot = 0

			result = await get_course_record(param)

			metadata['world_record']['best_time_pid'] = result.best_pid
			metadata['world_record']['first_complete_pid'] = result.first_pid
			metadata['world_record']['time_milliseconds'] = result.best_score
			metadata['world_record']['created_time'] = result.created_time.val
			metadata['world_record']['updated_time'] = result.updated_time.val

			# Get Mii data for the course creator, WR holder and first time completion

			param_creator = datastore_smm.DataStoreGetMetaParam()
			param_creator.data_id = 0
			param_creator.persistence_target = datastore_smm.DataStorePersistenceTarget()
			param_creator.persistence_target.owner_id = metadata['creator_pid']
			param_creator.persistence_target.persistence_id = 0
			param_creator.result_option = 4
			param_creator.access_password = 0

			param_world_record = datastore_smm.DataStoreGetMetaParam()
			param_world_record.data_id = 0
			param_world_record.persistence_target = datastore_smm.DataStorePersistenceTarget()
			param_world_record.persistence_target.owner_id = metadata['world_record']['best_time_pid']
			param_world_record.persistence_target.persistence_id = 0
			param_world_record.result_option = 4
			param_world_record.access_password = 0

			param_first_complete = datastore_smm.DataStoreGetMetaParam()
			param_first_complete.data_id = 0
			param_first_complete.persistence_target = datastore_smm.DataStorePersistenceTarget()
			param_first_complete.persistence_target.owner_id = metadata['world_record']['first_complete_pid']
			param_first_complete.persistence_target.persistence_id = 0
			param_first_complete.result_option = 4
			param_first_complete.access_password = 0

			params = [param_creator, param_world_record, param_first_complete]

			result = await datastore_smm_client.get_metas_multiple_param(params)

			mii_data_creator = result.infos[0]
			mii_data_world_record = result.infos[1]
			mii_data_first_complete = result.infos[2]

			metadata['miis']['creator']['nnid'] = mii_data_creator.name
			metadata['miis']['creator']['mii_data'] = base64.b64encode(mii_data_creator.meta_binary).decode('utf8')

			metadata['miis']['world_record']['nnid'] = mii_data_world_record.name
			metadata['miis']['world_record']['mii_data'] = base64.b64encode(mii_data_world_record.meta_binary).decode('utf8')

			metadata['miis']['first_complete']['nnid'] = mii_data_first_complete.name
			metadata['miis']['first_complete']['mii_data'] = base64.b64encode(mii_data_first_complete.meta_binary).decode('utf8')

			# Download course and save metadata to disk

			response = await http.get(course_data_url, headers=headers)

			course_data_file = open('./courses/course-%d.bin' % course_id, 'wb')
			course_data_file.write(response.body)
			course_data_file.close()

			metadata_file = open('./courses/course-%d-metadata.json' % course_id, 'w', encoding='utf-8')
			json.dump(metadata, metadata_file, ensure_ascii=False, indent=4)
			metadata_file.close()

			print('Saved course ID %d' % course_id)
		except:
			print('Failed to get course %d' % course_id)
			pass

#########################################################
# Not implemented in NintendoClients, implementing here #
#########################################################

class DataStoreGetCustomRankingByDataIdParam(common.Structure):
	def __init__(self):
		super().__init__()
		self.application_id = None
		self.data_id_list = None
		self.result_option = None
	
	def load(self, stream):
		self.application_id = stream.u32()
		self.data_id_list = stream.list(stream.u64)
		self.result_option = stream.u8()
	
	def save(self, stream):
		stream.u32(self.application_id)
		stream.list(self.data_id_list, stream.u64)
		stream.u8(self.result_option)

class DataStoreCustomRankingResult(common.Structure):
	def __init__(self):
		super().__init__()
		self.order = None
		self.score = None
		self.meta_info = None
	
	def load(self, stream):
		self.order = stream.u32()
		self.score = stream.u32()
		self.meta_info = stream.extract(datastore_smm.DataStoreMetaInfo)
	
	def save(self, stream):
		stream.u32(self.order)
		stream.u32(self.score)
		stream.add(self.meta_info)

class DataStoreGetCourseRecordParam(common.Structure):
	def __init__(self):
		super().__init__()
		self.data_id = None
		self.slot = None
	
	def load(self, stream):
		self.data_id = stream.u64()
		self.slot = stream.u8()
	
	def save(self, stream):
		stream.u64(self.data_id)
		stream.u8(self.slot)

class DataStoreGetCourseRecordResult(common.Structure):
	def __init__(self):
		super().__init__()
		self.data_id = None
		self.slot = None
		self.first_pid = None
		self.best_pid = None
		self.best_score = None
		self.created_time = None
		self.updated_time = None
	
	def load(self, stream):
		self.data_id = stream.u64()
		self.slot = stream.u8()
		self.first_pid = stream.u32()
		self.best_pid = stream.u32()
		self.best_score = stream.s32()
		self.created_time = stream.datetime()
		self.updated_time = stream.datetime()
	
	def save(self, stream):
		stream.u64(self.data_id)
		stream.u8(self.slot)
		stream.u32(self.first_pid)
		stream.u32(self.best_pid)
		stream.s32(self.best_score)
		stream.datetime(self.created_time)
		stream.datetime(self.updated_time)

async def get_custom_ranking_by_data_id(param):
	#--- request ---
	stream = streams.StreamOut(datastore_smm_client.settings)
	stream.add(param)
	data = await datastore_smm_client.client.request(datastore_smm_client.PROTOCOL_ID, 50, stream.get())

	#--- response ---
	stream = streams.StreamIn(data, datastore_smm_client.settings)

	obj = rmc.RMCResponse()
	obj.ranking_result = stream.list(DataStoreCustomRankingResult)
	obj.results = stream.list(common.Result)

	return obj

async def get_course_record(param):
	#--- request ---
	stream = streams.StreamOut(datastore_smm_client.settings)
	stream.add(param)
	data = await datastore_smm_client.client.request(datastore_smm_client.PROTOCOL_ID, 72, stream.get())

	#--- response ---
	stream = streams.StreamIn(data, datastore_smm_client.settings)

	result = stream.extract(DataStoreGetCourseRecordResult)

	return result

anyio.run(main)