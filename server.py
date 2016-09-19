#imports
import pymzn
import os
import re
from subprocess import Popen, PIPE, STDOUT
from flask import Flask, json, Response, request, render_template
from flask_socketio import SocketIO, emit

#setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

#sockets
socketio = SocketIO(app)

#REST
folder = 'models' #where the .mzn files are stored
models = []
for file in os.listdir(folder):
	if file.endswith('.mzn'):
		models.append(file)

def FindArgs(model):
	args = dict()
	file = open(folder + "/" + model + ".mzn")
	for line in file:
		line = line.split('%', 1)[0]
		if re.compile("^.*:.\w+;").match(line) and line.find("var") == -1 and line.find("set") == -1: #outputs have a var
			tokens = re.compile('\w+').findall(line)
			if (tokens[0] == 'array'):
				args[tokens[-1]] = 'array(' + tokens[-2] + ')'
			else:
				args[tokens[-1]] = tokens[-2]

	return args

@app.route('/models')
def Allmodels():
	return json.jsonify(models=models)

@app.route('/models/<string:model>')
@app.route('/models/<string:model>.mzn')
@app.route('/models/<string:model>.json')
def Arguments(model):
	if (model+".mzn" in models):
		tmpArgs = FindArgs(model)
		return json.jsonify(tmpArgs)
	else:
		return json.jsonify(model="no model found")

#REST
#inputs models musn't 'output'
@app.route('/solve/<string:model>')
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
						solution = str(pymzn.parse_dzn(line)).replace('\'', '\"') #use pymzn to turn output into nice JSON objects
						yield solution
		return Response(output_line(),  mimetype='text/json')
	else:
		return json.jsonify(model="no model found")

# TODO: Unsure if this is safe security wise, have to look into it.
# aka. CORS request.
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

#sockets
@app.route('/stream/<string:model>')
def stream(model):
	arguments = {
		'model': model,
	}
	for arg in request.args.keys():
		arguments[arg] = request.args.get(arg)
	return render_template('index.html', **arguments)

@socketio.on('request_solution')
def request_solution(data):
	#data must have 'model' attribute
	mzn_args = ''
	for arg in data:
		if arg != 'model':
			mzn_args += str(arg) + "=" + str(data[arg]) + ";"
	with Popen(["minizinc", folder + '/' + data['model']+".mzn", "-a", "-D",mzn_args],
		stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p: #-a outputs all solutions
		for line in p.stdout:

			markup = ['----------','==========']
			if line.rstrip() not in markup: #each new solution is a new JSON object
				solution = str(pymzn.parse_dzn(line)).replace('\'', '\"') #use pymzn to turn output into nice JSON objects
				emit('solution', solution, broadcast=True)

#run
if __name__ == '__main__':
	socketio.run(app)
