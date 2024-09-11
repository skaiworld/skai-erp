#!/usr/bin/env python

import os
import io
import time
import sys

def configure_synapse():
	import yaml

	isFresh = not os.path.isfile( '/data/homeserver.yaml' )

	if isFresh:
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

	config['user_directory'] = {
		'enabled': True,
		'search_all_users': True,
		'prefer_local_users': True,
		'show_locked_users': True,
	}

	config['auto_join_rooms'] = [
		f"#all:{os.environ['SYNAPSE_SERVER_NAME']}"
	]

	config['public_baseurl'] = os.environ['SYNAPSE_SERVER']
	config['autocreate_auto_join_rooms_federated'] = False
	config['autocreate_auto_join_room_preset'] = 'public_chat'
	config['auto_join_mxid_localpart'] = os.environ['SYNAPSE_ADMIN']
	config['enable_registration'] = False
	config['enable_3pid_lookup'] = True
	config['allow_guest_access'] = False

	config['email'] = {
		'smtp_host': os.environ['SYNAPSE_SMTP_HOST'],
		'smtp_user': os.environ['SYNAPSE_SMTP_USER'],
		'smtp_pass': os.environ['SYNAPSE_SMTP_PASS'],
		'force_tls': True,
		'app_name': 'SKAI Chat',
		'notif_from': f"%(app)s <{os.environ['SYNAPSE_SMTP_USER']}>",
		'enable_notifs': True,
		'client_base_url': f"https://{os.environ['SYNAPSE_SERVER_NAME']}/element",
		'invite_client_location': f"https://{os.environ['SYNAPSE_SERVER_NAME']}/element",
	}

	config['default_identity_server'] = 'https://vector.im'
	config['account_threepid_delegates'] = {
		'msisdn': 'https://vector.im'
	}

	with io.open( '/data/homeserver.yaml', 'w', encoding='utf8' ) as ofile:
		yaml.dump( config, ofile, default_flow_style=False, allow_unicode=True )

	time.sleep(10)

	if isFresh:
		try:
			os.system( 'register_new_matrix_user -c /data/homeserver.yaml -u $SYNAPSE_ADMIN -p $SYNAPSE_PASSWORD -a http://synapse:8008' )
		except:
			print( 'Admin registration failed. Register manually.' )

def configure_element():
	import json

	config = {}
	fpath = '/home/frappe/frappe-bench/apps/skaiui/skaiui/www/element/config.json'
	print( 'Updating Element config file' )
	with open( fpath, 'r' ) as f:
		config = json.load(f)

	config['brand'] = 'SKAI Chat'
	config['default_server_config']['m.homeserver'] = {
		'base_url': os.environ['SYNAPSE_SERVER'],
		'server_name': 'SKAI Chat Server'
	}
	config['branding'] = {
		'welcome_background_url': '/assets/skaiui/images/gradient-bg.svg',
		'auth_header_logo_url': '/assets/skaiui/images/skai-logo.svg',
		'auth_footer_links': [
            { "text": "Desk", "url": "https://desk.skaiworld.com" },
            { "text": "Docs", "url": "https://desk.skaiworld.com/docs/home" }
        ]
	}

	with open( fpath, 'w', encoding='utf-8' ) as ofile:
		json.dump( config, ofile, ensure_ascii=False, indent=4 )

if __name__ == "__main__":
	if ( sys.argv[ -1 ] == 'element' ):
		configure_element()
	else:
		configure_synapse()
