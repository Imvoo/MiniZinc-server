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
	output = [dict(),dict()] #[0] are inputs, [1] are outputs
	file = open(folder + "/" + model + ".mzn")
	for line in file:
		line = line.split('%', 1)[0]
		if re.compile("^.*:.\w+;").match(line):
			if line.find("var") == -1: #an input
				tokens = re.compile('\w+').findall(line)
				if (tokens[0] == 'array'):
					output[0][tokens[-1]] = 'array(' + tokens[-2] + ')'
				else:
					output[0][tokens[-1]] = tokens[-2]
			else: #an output
				tokens = re.compile('\w+').findall(line)
				if (tokens[0] == 'array'):
					output[1][tokens[-1]] = 'array(' + tokens[-2] + ')'
				else:
					output[1][tokens[-1]] = tokens[-2]


	return output

@app.route('/models')
def Allmodels():
	return json.jsonify(models=models)

@app.route('/models/<string:model>')
@app.route('/models/<string:model>.mzn')
@app.route('/models/<string:model>.json')
def Arguments(model):
	if (model+".mzn" in models):
		tmpArgs = FindArgs(model)[0]
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
	print(mzn_args)
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
	args = data['args'].split('&')[:-1]
	for arg in args:
		arg = arg.split('=')
		if arg[0] != 'model':
			mzn_args += str(arg[0]) + "=" + str(arg[1]) + ";"
	with Popen(["minizinc", folder + '/' + data['model']+".mzn", "-a", "-D",mzn_args],
		stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p: #-a outputs all solutions
		for line in p.stdout:

			markup = ['----------','==========']
			if line.rstrip() not in markup: #each new solution is a new JSON object
				solution = str(pymzn.parse_dzn(line)).replace('\'', '\"') #use pymzn to turn output into nice JSON objects
				socketio.emit('solution', solution)

#run
if __name__ == '__main__':
	socketio.run(app)
