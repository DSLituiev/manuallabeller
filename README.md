
## Installation

clone repository from your terminal:

    git clone https://github.com/DSLituiev/manuallabeller

if you are going to use the app with a remote image server, have it on your server as well.

## Running the app with a remote server

From your local machine, log into the server with port forwarding:

    # set server ip/dns address here
    SERVER=
    ssh -L 5000:localhost:5000 $SERVER

    
This way you got to the server side and port forwarding has been established. Now you need to launch the flask server
that will serve images:

    # go to the repository directory
    # within this directory run:
    bash runserver.sh


Open another terminal window (client side / your computer). Go to this repo directory and run:

    python3 multilbl.py

The app window will appear. The app will read images from the server, present them, and save locally labels you provide.

## Configuration file
configuration is stored in `config.yaml` with following fields:

    indir: "data"                   # directory where data lives
    meta : 'path-to/filelist.txt'   # list of files to be presented (relative to `indir`)
    logfile : "labels.txt"          # file where results (labels) are stored
    url: '127.0.0.1:5000'           # remove if data is local
    symbols:                        # ordered list of label symbols that are cycled by mouse click
     - E
     - T
     - X
     - W
     - ''                          # last label is the default label
