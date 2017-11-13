SERVER=`grep 'server' config.yaml | cut -f2 -d":" | sed "s/'//g" | sed 's/ //g'`
ssh -L 5000:localhost:5000 $SERVER
