
# A tool for manual labelling of images

## Requirements
the script runs on `python3` and uses `pyglet` module.

## Commands
Press any key to start the session. On every image, press a key to label it. You can go to the previous image using backspace key. Escape key stops the session. Any stopped session will be reopened to continue with the image following one that was presented last in the previous session.

## Setting paths

You'll have to set the `indir` parameter (path to the image directory) in one of the last lines of the script.
It writes the key you press to the file `logfile`.


