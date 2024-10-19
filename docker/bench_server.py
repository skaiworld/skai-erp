#!/usr/bin/env python

import shlex
import time
import json
import os
import errno
from subprocess import Popen, PIPE, STDOUT
from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl, urlparse
from inspect import signature
from http.server import HTTPServer

# Constants
URL_BASE = '/skaibench'
SESSION_LIFE = 3600

# Environment variable
# BENCH_SECRET
# ADMIN_PASSWORD

# Global Variables
url_rules = {}
outputs = []

class Session:
	ids = {}

	def backend_logged_in(address, sid):
		# Todo: HTTPSConnection
		from http.client import HTTPConnection
		try:
			c = HTTPConnection(address)
			c.request('GET', '/api/method/skaiui.api.get_logged_roles', headers={'Cookie': f'sid={sid}'})
			r = c.getresponse()
			return r.status == 200 and ('System Manager' in json.loads(r.read().decode('utf-8'))['message'])
		except:
			return False
		finally:
			c.close()

	def logged_in(skid):
		for i, t in list(Session.ids.items()):
			if int(time.time()) > t:
				del Session.ids[i]
		return skid in Session.ids

	def login(un, pw):
		if(un.lower() == 'administrator' and pw == os.environ['ADMIN_PASSWORD']):
			import hashlib
			skid = hashlib.md5(f'{un}:{os.environ["BENCH_SECRET"]}'.encode()).hexdigest()
			Session.ids[skid] = int(time.time()) + SESSION_LIFE
			return skid

class Handler(BaseHTTPRequestHandler):
	@cached_property
	def url(self):
		return urlparse(self.path)

	@cached_property
	def query_data(self):
		return dict(parse_qsl(self.url.query))

	@cached_property
	def post_data(self):
		content_length = int(self.headers.get('Content-Length', 0))
		return self.rfile.read(content_length)

	@cached_property
	def form_data(self):
		return dict(parse_qsl(self.post_data.decode('utf-8')))

	@cached_property
	def cookies(self):
		return SimpleCookie(self.headers.get('Cookie'))

	def do_GET(self):
		self.res_code = 200
		self.res_cookie = SimpleCookie()
		self.res_headers = {}
		self.res_content = ''
		self.process()
		self.send_response(self.res_code)
		for k,v in self.res_headers.items():
			self.send_header(k, v)
		for morsel in self.res_cookie.values():
			self.send_header('Set-Cookie', morsel.OutputString())
		self.end_headers()
		self.wfile.write(self.res_content)

	def do_POST(self):
		self.do_GET()

	def set_cookie(self, k, v='', meta={}):
		self.res_cookie[k] = v
		for mk, mv in meta.items():
			self.res_cookie[k][mk] = mv

	def set_header(self, k, v):
		self.res_headers[k] = v

	def set_content(self, c):
		self.res_content = c.encode('utf-8')

	def process(self):
		content = 'Not found'
		sub_path = self.url.path.replace(URL_BASE if URL_BASE.endswith('/') else f'{URL_BASE}/', '/', 1)
		if (URL_BASE in self.url.path and sub_path in url_rules):
			args = [ self ] if url_rules[sub_path]['len'] else []
			content = url_rules[sub_path]['func']( *args )
		self.set_content( content )
		return

def pid_exists(pid):
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False
        elif err.errno == errno.EPERM:
            return True
        else:
            raise
    else:
        return True

def route(rule):
	def wrapper(f):
		url_rules[rule] = {'func': f, 'len': len(signature(f).parameters)}
	return wrapper

def auth(f):
	def wrapper(*args, **kwargs):
		h = args[0]
		sid = h.cookies['sid'].value if ('sid' in h.cookies) else None
		skid = h.cookies['skid'].value if ('skid' in h.cookies) else None

		# If login form submit, set session
		if ('un' in h.form_data and 'pw' in h.form_data):
			skid = Session.login(h.form_data['un'], h.form_data['pw'])
			h.set_cookie('skid', skid, {'max-age': SESSION_LIFE, 'path': URL_BASE})

		# If not logged in, show login form
		address = os.environ['ADDRESS'] if 'ADDRESS' in os.environ else f'{h.headers["Host"]}:8080'
		if not Session.backend_logged_in(address, sid) and not Session.logged_in(skid):
			h.set_header('Content-Type', 'text/html; charset=utf-8')
			return '''<form method="post"><input placeholder="Username" name="un">
				<input type="password" placeholder="Password" name="pw">
				<button type="submit">Login</button></form>'''

		# Continue to execute the wrapped function
		args = args[:len(signature(f).parameters)]
		return f(*args, **kwargs)
	return wrapper

def run_command(cmd):
	# Clear old
	global outputs
	outputs = [op for op in outputs if ((op['start'] + 7200) > int(time.time()))]
	ALLOWED_COMMANDS = [
		'bench migrate',
		'bench build'
	]
	pid = 0
	if (cmd.startswith('skaicust ')):
		cmd = cmd[9:]
	elif (cmd not in ALLOWED_COMMANDS):
		cmd = None
	if cmd:
		try:
			proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=STDOUT, text=True)
		except OSError:
			return pid
		pid = proc.pid
		outputs.append({
			'cmd': cmd,
			'proc': proc,
			'start': int(time.time()),
			'stdout': '',
		})
	return pid

@route('/')
@auth
def home(h):
	'''
	Input Params Eg:
	h.url.path,
	h.query_data,
	h.post_data.decode("utf-8"),
	h.form_data,
	h.res_cookie.output(header="").strip(),

	Set Output Eg:
	h.set_header('Content-Type', 'application/json')
	h.set_cookie('key', 'val', {'max-age': 5})
	h.set_content( 'Home' ) OR return 'Home'
	'''
	h.set_header('Content-Type', 'text/html; charset=utf-8')
	result = ''
	if ('command' in h.form_data):
		cmd = h.form_data['command']
		result = f'Running command: {cmd}, PID: {run_command(cmd)}'

	script = '''
	function getOPs() {
		fetch('outputs').then(r => r.json())
		.then(ops => {
			let content = ''
			for (const op of ops) { content += `<pre style="color: #fff; background: #17242f; position: relative; padding:0 10px 10px; max-height: 1000px; overflow: auto;"><div style="position: sticky !important; top: 0; background:#000;display:flex;justify-content:space-between;padding:5px 10px;margin:0 -10px 5px;"><i>Command: ${op.cmd}</i><i>PID: ${op.pid}</i><i>Status: ${op.status}</i></div>${op.stdout}</pre>` }
			document.getElementById('ops').innerHTML = content
		})
	}
	getOPs()
	setInterval(getOPs, 10000)
	'''

	return f'''<div>Dashboard</div>
	<div>Run bench command</div>
	<div><form method="post">
		<input placeholder="Bench Command" name="command">
		<button type="submit">Run</button>
	</form>
	<div id="result">{result}</div><div id="ops"></div></div>
	<script type="text/javascript">{script}</script>
	'''

@route('/outputs')
def get_outputs(h):
	h.set_header('Content-Type', 'application/json')
	r = []
	for op in outputs:
		os.set_blocking(op['proc'].stdout.fileno(), False)
		op['stdout'] += ''.join(op['proc'].stdout.readlines())
		op['proc'].poll()
		r.append({
			'pid': op['proc'].pid,
			'cmd': op['cmd'],
			'start': op['start'],
			'stdout': op['stdout'],
			'status': 'Running' if op['proc'].returncode is None else 'Done',
		})
	return json.dumps(r)

if __name__ == "__main__":
	server = HTTPServer(('0.0.0.0', 8006), Handler)
	print( 'Starting server on localhost:8006' )
	try:
		server.serve_forever()
	except Exception as e:
		print( e )
	except:
		print( '\nServer stopped' )
