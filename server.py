#imports
import pymzn
import os
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


@app.route('/stream')
def stream():
	return render_template('index.html')

 
#why doesn't this run?   
@socketio.on('request template')
def request_template(model):
	with Popen(["minizinc", folder + '/' + model+".mzn", "-a", "-D"], stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p: #-a outputs all solutions
		for line in p.stdout:
			markup = ['----------','==========']
			if line.rstrip() not in markup: #each new solution is a new JSON object
				solution = str(pymzn.parse_dzn(line)).replace('\'', '\"') #use pymzn to turn output into nice JSON objects
				emit('solution', solution, broadcast=True)
					
#run
if __name__ == '__main__':
	socketio.run(app)
