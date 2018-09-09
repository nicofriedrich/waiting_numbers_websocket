##WaitNumbersModul
# coding: utf8
#  Server containts a singleton object and Server. This is a StandAlone tornado
#  WebApplication Server. It has @gen / Async Librarys and tormysql includes
#  which allows an Async Process for fast End to End connections
#  @author Nico friedrich
#  @copyright fpsVisionary Software
import tornado.websocket
from collections import OrderedDict
import json,time,uuid,sys
from time import sleep
from time import gmtime, strftime
wss = []
## NOTE: Problems with utf8 coding dirty fix!
reload(sys)
sys.setdefaultencoding('utf8')

## WebSocketWaitNumbersHandler - subclasses WebSocketHandler
#  This is the main Handler for incoming and outgoing websocket messages
#  It specify the websocket wether is (LIST/Pickup Client or WAIT / WaitSystem Client)
class WebSocketWaitNumbersHandler(tornado.websocket.WebSocketHandler):
    ##give every connection a uuid
    uuid = None
    ##declares the msgType (WAIT or LIST) TODO:more to come
    msgType = None
    ## initialize - function
    #  inits the websocket and sets the server obj
    #  @param self obj WebSocketHandler
    #  @param server obj Server Obj
    def initialize(self, server):
        self.server = server

    ## open - function
    #  on Open the websocket
    #  @param self obj WebSocketHandler
    def open(self):
        if self not in wss:
            #only add websocket if there is no in dict
            wss.append(self)
        self.uuid = uuid.uuid4()
        print 'new connection'

    ## explicit_close - function
    #  on explicit close the websocket
    #  @param self obj WebSocketHandler
    def explicit_close(self):
        wss.remove(self)
        print 'closed connection'
        self.isOpen = False
        self.close() # you wont even have to iterate over the clients.
    
    ## explicit_close - function
    #  on message of the websocket called when send a message from client
    #  @param self obj WebSocketHandler
    #  @param message string Message string
    def on_message(self, message):
        # Declare Response dict
        response = {}
        response['is_error'] = 0
        if message == "LIST" or message == "WAIT":
            #This is LIST or WAIT Hello
            if not self.msgType:
                #Set the msgType of WebSocket
                self.msgType = message
            if len(self.server.contacts) > 0:
                #If there are already contacts  => send them in the response
                response['entity'] = "Contacts"
                response['action'] = "get"
                response['values'] = self.server.contacts
        elif "PickupContact" in message:
            #this is when Employer scans or closes a client
            try:
                #this is the req from pickup
                req = json.loads(message)
                response = self.handleContact(req)
            except Exception as e:
                response['is_error'] = 1
                response['error_message'] = str(e)
            
        else:
            ##on regulary not dict packed objects
            #TODO: this is not so good :-( pack this also in a readable dict (json)
            try:
                self.server.contacts = json.loads(message)
                response['entity'] = "Contacts"
                response['action'] = "post"
                if len(self.server.contacts) > 0:
                    res = {}
                    res['is_error'] = 0
                    res['entity'] = "Contacts"
                    res['action'] = "get"
                    res['values'] = self.server.contacts
                    for ws in wss:
                        if(ws.msgType == "WAIT"):
                            ws.write_message(json.dumps(res))

            except Exception as e:
                response['is_error'] = 1
                response['error_message'] = str(e)
        
        self.write_message(json.dumps(response))
       
    ## on_close - function
    #  on close the websocket
    #  @param self obj WebSocketHandler
    def on_close(self):
        wss.remove(self)
        self.close()
        print 'connection closed'

    ## check_origin - function
    #  wether origin should be checked or not
    #  @param self obj WebSocketHandler
    #  @param origin bool
    #  @return bool 
    def check_origin(self, origin):
        return True

    ## handleContact - function
    #  hanlde the contact find and delete on current or close
    #  @param self obj WebSocketHandler
    #  @param req dict
    #  @return dict 
    def handleContact(self,req):
        response = {}
        response['is_error'] = 0
        response['entity'] = req['entity']
        response['action'] = req['action']
        pContact = req['values']
        found = False
        #look for our contact
        idx = None
        for aContact in self.server.contacts:
            if aContact['id'] == pContact['id']:
                idx = self.server.contacts.index(aContact)
                found = True
            
        if req['action'] == "start":
            #customer on pickup place (scanned)
            if found:
                self.server.current[idx] = req['cash']
                for ws in wss:
                    if(ws.msgType == "WAIT"):
                        res = {'is_error':0}
                        res['entity'] = "PickupContact"
                        res['action'] = "current"
                        res['current'] = self.server.current
                        ws.write_message(json.dumps(res))

        if req['action']  == "close":
            del self.server.current[idx]
            del self.server.contacts[idx]
            for ws in wss:
                if(ws.msgType == "WAIT"):
                    res = {'is_error':0}
                    res['entity'] = "PickupContact"
                    res['action'] = "close"
                    res['current'] = idx
                    ws.write_message(json.dumps(res))
            #costumer was closing and can be deleted from current and complete array
        if not found:
            response['is_error'] = 1
            response['error_message'] = "Kontakt konnte nicht im WarteSystem gefunden werden."

        return response

