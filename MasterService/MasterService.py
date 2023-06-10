import tornado
from MasterService.Logging import *
from MasterService.MasterDomain import MasterDomain
import tornado.ioloop
import tornado.web
import json
from tornado.gen import coroutine

import json

class AddMessageHandler(tornado.web.RequestHandler):
    @coroutine
    def post(self):
        try:
            data = json.loads(self.request.body)
            service_log("POST request! With new message: " + data["message"])
            domain = MasterDomain()
            res = yield domain.add_message(data["message"], data["write-concern"])
            if (res):
                self.set_status(200)
            else:
                self.set_status(500)
            self.write("")
        except Exception as e:
            self.set_status(500)
            self.write("Error: " + str(e))

class RegisterHandler(tornado.web.RequestHandler):
    @coroutine
    def post(self):
        try:
            data = json.loads(self.request.body)
            service_log("POST request! With new message: " + data["ip"]+":"+data["port"])
            domain = MasterDomain()

            messages = yield domain.add_client(data["ip"]+":"+data["port"])
            self.set_status(200)
            self.write(json.dumps(messages))
        except Exception as e:
            self.set_status(500)
            self.write("Error: " + str(e))

class GetMessageHandler(tornado.web.RequestHandler):
    @coroutine
    def get(self):
        try:
            service_log("GET request!")
            domain = MasterDomain()
            self.write(json.dumps((yield domain.get_messages())))
        except Exception as e:
            self.set_status(500)
            self.write("Error: " + str(e))
