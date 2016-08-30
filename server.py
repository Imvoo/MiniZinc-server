import pymzn
import os
from subprocess import Popen, PIPE
from flask import Flask, json, Response, request
app = Flask(__name__)

folder = 'models' #where the .mzn files are stored
models = []
for file in os.listdir(folder):
	if file.endswith('.mzn'):
		models.append(file)

def FindInputs(model):
	print("modelzzdszd")
	with Popen(["minizinc", folder + '/' + model], stdout=PIPE, bufsize=1, universal_newlines=True) as p:
		for line in p.stdout:
			print("newlin")
			print(line)
			print (str(line))
			yield line

@app.route('/inputs/<string:model>')
def GetInputs(model):
	print(model)
	model = model + ".mzn"
	if model in models:
		print("Finding")
		a = FindInputs(model)
		return Response(a)
		return ""
	return ""

@app.route('/')
def Allmodels():
	return json.jsonify(result=models)

#inputs models musn't 'output'
@app.route('/model/<string:model>.json')
def Model(model):
	# TODO: Pass n / other arguments to minizinc.
	n = request.args.get('n')

	if (model+".mzn" in models):
		def output_line():
			# TODO: Abstract input parsing.
			# Maybe if we passed in the inputs in the query, e.g. inputs = request.args.get('inputs').
			# That will be passed as maybe an array or something, then we just iterate over the array
			# 	and give it to minizinc with "-D", input[i] + "=" + actual value.
			# 	E.g. if input[0] = 'n',
			# 	process.append("-D")
			# 	process.append(input[0] + "=" + n)
			with Popen(["minizinc", folder + '/' + model+".mzn", "-a", "-D", "n=" + n], stdout=PIPE, bufsize=1, universal_newlines=True) as p: #-a outputs all solutions
				for line in p.stdout:
					markup = ['----------','==========']
					if line.rstrip() not in markup: #each new solution is a new JSON object
						yield str(pymzn.parse_dzn(line)).replace('\'', '\"') #use pymzn to turn output into nice JSON objects
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
