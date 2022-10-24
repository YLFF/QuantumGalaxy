from xml.dom.pulldom import default_bufsize
from tornado.httpserver import HTTPServer
from tornado.wsgi import WSGIContainer
from flask_server_82 import *
from tornado.ioloop import IOLoop
from tornado import gen


import time


def block(num):
    while True:
        print(num)
        time.sleep(2)
async def loop(name):
    while True:
        print(name)
        await gen.sleep(1)
s = HTTPServer(WSGIContainer(app))
s.listen(82) 
io = IOLoop.current()
#io.run_in_executor(None, block, "run_in_executor")
#io.add_callback(loop, "add_callback")
#io.spawn_callback(loop, "spawn_callback")
io.start()


