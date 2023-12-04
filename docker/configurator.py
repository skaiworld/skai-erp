#!/usr/bin/env python

import os
import io
import time
import yaml

def configure():
	if os.path.isfile( '/data/homeserver.yaml' ):
		return

	print( 'Generating config file' )
	os.system( 'python3 start.py generate' )

	config = {}
	print( 'Updating config file' )
	with open( '/data/homeserver.yaml', 'r' ) as stream:
		config = yaml.safe_load(stream)

	config['database'] = {
		'name': 'psycopg2',
		'args': {
			'user': 'synapse',
			'password': os.environ['PG_PASSWORD'],
			'database': 'synapse',
			'host': 'postgres',
			'cp_min': 5,
			'cp_max': 10
		}
	}

	with io.open( '/data/homeserver.yaml', 'w', encoding='utf8' ) as outfile:
		yaml.dump( config, outfile, default_flow_style=False, allow_unicode=True )

	time.sleep(10)
	try:
		os.system( 'register_new_matrix_user -c /data/homeserver.yaml -u $SYNAPSE_ADMIN -p $SYNAPSE_PASSWORD -a http://synapse:8008' )
	except:
		print( 'Admin registration failed. Register manually.' )

if __name__ == "__main__":
	configure()
