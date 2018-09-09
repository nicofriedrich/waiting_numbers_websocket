#!/usr/bin/env python
# coding: utf8
## @package ServerPackage
#  Server containts a singleton object and Server. This is a StandAlone tornado
#  WebApplication Server. It has @gen / Async Librarys and tormysql includes
#  which allows an Async Process for fast End to End connections
#  @author Nico friedrich
#  @copyright fpsVisionary Software
__version__ = '0.9.45'
__revision__ = {
    "revision":"$Rev: 1482 $",
    "last_user_modified":"$Author: n.friedrich $",
    "last_modified":"$Date: 2017-07-17 11:22:57 +0200 (Mo, 17 Jul 2017) $"
}
import tornado.ioloop
import tornado.web
import wait_numbers as waitNumbersModul
import json, pprint, sys, os, hashlib, logging


## Singleton Handling for a SEngine.\n
#  everytime you need the engine main object call:\n
#  engine = SEngine(0,0) # matrix (32,32) is unnecessary when already initiated
#  @return class (class) - returns the current class or the instance of it
def singleton(class_):
    class class_w(class_):
        _instance = None
        def __new__(class2, *args, **kwargs):
            if class_w._instance is None:
                class_w._instance = super(class_w, class2).__new__(class2, *args, **kwargs)
                class_w._instance._sealed = False
            return class_w._instance
        def __init__(self, *args, **kwargs):
            if self._sealed:
                return
            super(class_w, self).__init__(*args, **kwargs)
            self._sealed = True
    class_w.__name__ = class_.__name__
    return class_w

## Server - subclasses Bottle > Web/Rest API Module
#  infinity run with app.run(host='localhost', port=8080)
#  holds the following Objects:
#  user_ids and tokens
#  contacts (the customers)
#  current a dict of how is current
#  It has direct connection to original drupal db and calistix_db
@singleton
class Server(object):
    contacts = []
    current = {}
    ## tornadoApp Object(Server) present
    tornadoApp = None
    def __init__(self, name, region):
        print "init server"
        print __version__
        print __revision__['revision']

    def make_app(self):
        script_path = os.path.dirname(__file__)
        self.app = tornado.web.Application([
            (r"/ws/wait_numbers", waitNumbersModul.WebSocketWaitNumbersHandler,dict(server=self)),
        ])
        return self.app

## Starts the main Sever
if __name__ == "__main__":
    server = Server('WaitNumbers',"localhost")
    server.make_app()
    server.app.listen(4438)
    tornado.ioloop.IOLoop.current().start()
