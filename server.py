import os
from flask import Flask, Response, request, send_from_directory
#from OpenSSL import SSL
#context = SSL.Context(SSL.SSLv23_METHOD)
#context.use_privatekey_file('yourserver.key')
#context.use_certificate_file('yourserver.crt')

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
datadir="data"
metadir = 'filelist'

@app.route('/{}/<path:path>'.format(datadir))
def send_js(path):
    return send_from_directory(datadir, path)

@app.route('/{}/<path:path>'.format(metadir))
def send_meta(path):
    return send_from_directory(metadir, path)

@app.route('/ls')
def send_ls():
    xml = '\n'.join(os.listdir('./{}/'.format(datadir)))
    print(Response(xml))
    return Response(xml, mimetype='text')

@app.route('/')
def hello_world():
    return '\n\nthis is a server of images for manual classification'

if __name__ == "__main__":
        app.run(host='0.0.0.0')


