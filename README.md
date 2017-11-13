
On client side, run:

    # set server ip/dns address here
    SERVER=
    ssh -L 5000:localhost:5000 $SERVER

    
Now you are on the server side:
    # go to the directory with the repository and data
    # within this directory run:
    bash runserver.sh


Open another terminal window, go to this directory and run:
    python3 multilbl.py

    


    
