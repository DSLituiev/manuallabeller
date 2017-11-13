#!/bin/bash

scrname='labeller'
if  [[ ! -z "$(screen -ls | grep $scrname)" ]]
then
	echo "a screen with the name '"$scrname"' is already running!"
	echo "if necessary, run:"
	echo "screen -R $scrname"
	echo "and detach from it (ctrl+D)"
	echo "or"
	echo "screen -X -S $scrname quit"
	echo "==========================="
	echo "exiting" && exit 1
fi

screen -Sdm $scrname bash -c "export FLASK_APP=server.py && flask run" || exit 1

if  [[  -z "$(screen -ls | grep $scrname)" ]]
then
	echo "failed to launch a flask server"
else
	echo "running a flask server for labelling in a detatched screen ('"$scrname"')"
fi
	
