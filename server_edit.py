import pymzn
import os
<<<<<<< Updated upstream
from subprocess import Popen, PIPE, STDOUT
=======
from subprocess import Popen, PIPE
<<<<<<< Updated upstream
>>>>>>> Stashed changes
from flask import Flask, json, Response, request
=======
from flask import Flask, json, Response, render_template
from flask.ext.socketio import SocketIO, emit


>>>>>>> Stashed changes
app = Flask(__name__)
socketio = SocketIO(app)

folder = 'models' #where the .mzn files are stored
models = []
for file in os.listdir(folder):
	if file.endswith('.mzn'):
		models.append(file)

@app.route('/')
def Allmodels():
	return json.jsonify(result=models)

#inputs models musn't 'output'
@app.route('/model/<string:model>.json')
def Model(model):
	mzn_args = ''
	for p in request.args.keys():
		mzn_args += str(p) + "=" + str(request.args.get(p)) + ";"

	if (model+".mzn" in models):
		def output_line():
			with Popen(["minizinc", folder + '/' + model+".mzn", "-a", "-D", mzn_args],
				stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p: #-a outputs all solutions
				for line in p.stdout:
					markup = ['----------','==========']
					if line.rstrip() not in markup: #each new solution is a new JSON object
						yield str(pymzn.parse_dzn(line)).replace('\'', '\"') #use pymzn to turn output into nice JSON objects
		return Response(output_line(),  mimetype='text/json')
	else:
		return json.jsonify(model="no model found")

<<<<<<< Updated upstream
# TODO: Unsure if this is safe security wise, have to look into it.
# aka. CORS request.
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response
=======

@socketio.on('value changed')
def value_changed(message):
    values[message['who']] = message['data']
    emit('update value', message, broadcast=True)

@app.route('/index')
def index():
	socket()
	return render_template('index.html')


def socket():
	with Popen(["MiniZinc", "models/test.mzn", "-a"], stdout=PIPE, bufsize=1, universal_newlines=True) as p: #-a outputs all solutions
		for line in p.stdout:
			markup = ['----------','==========']
			if line.rstrip() not in markup: #each new solution is a new JSON object
				socketio.emit('send_json',pymzn.parse_dzn(line)) #use pymzn to turn output into nice JSON objects

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
>>>>>>> Stashed changes
