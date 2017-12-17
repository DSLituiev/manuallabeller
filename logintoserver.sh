SERVER=`grep 'server' config.yaml | cut -f2 -d":" | sed "s/'//g" | sed 's/ //g'`
USER=`grep 'user' config.yaml | cut -f2 -d":" | sed "s/'//g" | sed 's/ //g'`
if [ ! -z "$USER" ]
then
    USER="$USER@"
fi

ssh -L 5000:localhost:5000 $USER$SERVER
