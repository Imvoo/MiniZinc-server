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

def FindArgsProper(model):
	directory = os.path.dirname(os.path.realpath(__file__))
	jsonArgs = ''
	with Popen(["mzn2fzn", "--model-interface-only", folder + '/' + model + ".mzn"],
		stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p: #-a outputs all solutions
		for line in p.stdout:
			jsonArgs += line

	return json.loads(jsonArgs)

@app.route('/get_template/<string:model>')
def GetTemplate(model):
	template = {
		"error": "no template found"
	}
	for file in os.listdir('app_templates'):
		if file == model + '.json':
			tempFile = open('./app_templates/' + model + '.json', 'r')
			template = json.load(tempFile)

	return json.jsonify(template)

@app.route('/save_template', methods=['GET', 'POST'])
def SaveTemplate():
	if not os.path.exists('./app_templates/'):
		os.makedirs('./app_templates/', exist_ok=True)

	file = open('./app_templates/' + request.json['name'] + '.json', 'w')
	json.dump(request.json, file, indent=4)
	file.close()

	return "Success"

@app.route('/models')
def Allmodels():
	return json.jsonify(models)

@app.route('/models/<string:model>')
@app.route('/models/<string:model>.mzn')
@app.route('/models/<string:model>.json')
def Arguments(model):
	if (model+".mzn" in models):
		tmpArgs = FindArgsProper(model)
		return json.jsonify(tmpArgs)
	else:
		return json.jsonify(error="no model found")

#REST
#inputs models musn't 'output'
@app.route('/solve/<string:model>')
def Model(model):
	mzn_args = ''
	for p in request.args.keys():
		mzn_args += str(p) + "=" + str(request.args.get(p)) + ";"

	if (model+".mzn" in models):
		def output_line():
			directory = os.path.dirname(os.path.realpath(__file__))
			realPath = directory + "/" + folder + "/" + model+".mzn"

			# TODO: change this into it's separate process / real path.
			with Popen(["minizinc", folder + "/" + model + ".mzn", "-a", "-D", mzn_args],
				stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p: #-a outputs all solutions
				for line in p.stdout:
					markup = ['----------','==========']
					if line.rstrip() not in markup: #each new solution is a new JSON object
						solution = str(pymzn.parse_dzn(line)).replace('\'', '\"') #use pymzn to turn output into nice JSON objects
						yield solution
		return Response(output_line(),  mimetype='text/json')
	else:
		return json.jsonify(error="no model found")

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

user_dict = dict()

@socketio.on('request_solution')
def request_solution(data):
	mzn_args = ''

	for key in data:
		if key != 'model':
			if 'dim' in data[key]:
				if data[key]['dim'] == 2:
					mzn_args += key + "=["
					for row in data[key]['value']:
						mzn_args += "| "
						mzn_args += ', '.join(map(str,row))
						mzn_args += ' '

					mzn_args += " |];"
			else:
				mzn_args += key + "=" + str(data[key]['value']) + ";"

	with Popen(["minizinc", folder + '/' + data['model']+".mzn", "-a", "-D",mzn_args],
		stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p: #-a outputs all solutions
		user_dict[request.sid] = p
		for line in p.stdout:

			markup = ['----------','==========']
			if line.rstrip() not in markup: #each new solution is a new JSON object
				solution = str(pymzn.parse_dzn(line)).replace('\'', '\"') #use pymzn to turn output into nice JSON objects
				send_solution(solution)

				#print(request.sid)
def send_solution(solution):
	socketio.emit('solution', solution)

@socketio.on('kill_solution')
def kill_solution():
	p = user_dict[request.sid]
	p.kill()

#run
if __name__ == '__main__':
	socketio.run(app)
