from flask import Flask, send_from_directory
from flask_cors import CORS
import json

rpath='E:\wangzhilin\QuantumGalaxy\server_qgfp\app\galaxy'
app = Flask(__name__,static_folder='dist',static_url_path="/dist")
app.config['JSON_AS_ASCII'] = False
CORS(app)
@app.route('/hello')
def test():
    return 'hi'
@app.route('/')
def serve_static_index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if path.startswith('css/') or path.startswith('js/')\
            or path.startswith('img/') or path.startswith('_nuxt/') or path == 'favicon.ico':
        return app.send_static_file(path)
    else:
        print(path)
        return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000,debug=True)