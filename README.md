# MiniZinc-server

<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [MiniZinc-server](#minizinc-server)
	- [Requirements](#requirements)
	- [Getting Started](#getting-started)
	- [Using MiniZinc-server](#using-minizinc-server)
		- [/](#)
				- [Overview](#overview)
				- [Parameters](#parameters)
				- [Sample Output](#sample-output)
		- [/models/\<modelName\>.json](#modelsmodelnamejson)
				- [Overview](#overview)
				- [Parameters](#parameters)

<!-- /TOC -->

## Requirements

- Python (>3.5)
- Pip
    - Should come pre-installed with Python 3.5.
- Flask
- Pymzn
- Minizinc
    - http://www.minizinc.org/software.html
    - Easiest method: grab the bundled binary package and add the folder to your environment variables/PATH.

## Getting Started

1. Assuming you have **python** and **pip** installed, run the following two commands in your cmd/terminal window:
    - `pip install flask`
    - `pip install pymzn`
2. After you have the dependencies installed, in order for Flask to run it needs to know what the server file is called.
    - The environment variable `FLASK_APP` needs to be set. To do this:
        - Windows: `set FLASK_APP=server.py`
        - Mac OSX/Linux: `export FLASK_APP=server.py`
3. In your terminal window, run `flask run` to start the server.
4. The server should be hosted on port 5000, by default at [http://localhost:5000](http://localhost:5000).

## Using MiniZinc-server

**NOTE: The REST API is formatted a little bit weirdly at the moment (not akin to a real REST API) this will be fixed in the future).**

The MiniZinc server solves certain MiniZinc files on the backend and returns the output as JSON in the form of a REST api. All the following URLs will be relative to the root URL, i.e. the REST api is accessed by appending certain URLs like `/models/queens.json?n=4` to `localhost:5000`.

### /
##### Overview
Returns the MiniZinc model files available in the server.

##### Parameters

- No parameters.

##### Sample Output

```
{
  "result": [
    "queens.mzn",
    "schedule.mzn",
    "test.mzn",
    "test2.mzn"
  ]
}
```

### /models/\<modelName\>.json

##### Overview
Solves the input MiniZinc model file in the backend.

##### Parameters

- `<modelName>`: the name of the MiniZinc model **(required)**.
- `n`: number of Queens to solve. (only applicable to Queens at the moment). **(required)**
