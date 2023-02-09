# VarLogSearch
An API server that returns REST according to the Open API specification. This is a demonstration server with the concept of specifying logs in /var/log and returning log lines found using search keywords in a list starting with the latest.

## Quickstart

#### Install python 
Install python 3.11.1 from https://www.python.org/downloads/release/python-3111/

#### Install pacakge and initialize app
```
$ pip install pipenv
$ pipenv --python 3.11.1 install --dev
$ pipenv shell
$ make init
```
#### Setup config
Set config file at `configs/config_dev.ini` if needed
```commandline
[api]
debug = false
log_file = ./logs/app_server_search.log
port = 8080
```

#### Run on local
```
python main.py
```

## How to develop

#### Install dev package
```
$ install_dev_package
```

#### Make mock log file
If you want to use your own log, please create it with the following script.
```
$ python scripts/make_log_file.py --help
usage: make_log_file.py [-h] [--filesize FILESIZE] [--filename FILENAME] [--keyword KEYWORD]
                        [--occurrences OCCURRENCES]

Make random log

options:
  -h, --help            show this help message and exit
  --filesize FILESIZE   an integer for file size. writes a log slightly larger than the specified size
  --filename FILENAME   an string for generating file location
  --keyword KEYWORD     an string for keyword
  --occurrences OCCURRENCES
                        Occurrence frequency of the word you want to insert
                        
```
Set the file location, size, words you want to include in the log line, and their frequency.
```
$ python scripts/make_log_file.py --filename=/tmp/random.log --filesize=1073741824 --keyword test -occurrences
```
If you are not the root user, use sudo to move the file to /var/log
```
$ sudo mv /temp/random.log /var/log
```
To fix the formatting of the code run the following command
```commandline
$ sudo make pretty
```
Run unittest
```
$ make unit
```

Run main.py in Pycharm or command line to start the service
```commandline
$ python main.py
```

## API Docs
Please check the Swagger URL below for the API.
http://localhost:8080/docs/api/v1/

Example of Postman config is [here](tools/varlogsearch.postman_collection.json "s/varlogsearch.postman_collection.json")

## Frontend
The basic UI is in the repository below, so if you want to access this server from the UI, please set up a front-end server according to the README in the repository below.
[VarLogSearchFrontend](https://github.com/sakaijunsoccer/varlogsearchfrontend)
