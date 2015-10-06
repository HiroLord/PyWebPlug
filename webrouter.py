# This file runs the websockets.

import string, cgi, time
import sys
sys.path.insert(0, 'PyWebPlug')
from wsserver import *

from time import sleep

def setupMessages():
    return


class Client:

    def __init__(self, socket):
        self.socket = socket
        self.needsConfirmation = True
        self.name = "Name"
    
    def handle(self):
        data = ""
        if (self.socket):
            try:
                data = self.socket.readRaw()
                if (data == None):
                    return self.disconnect()
            except:
                self.socket = None
        if len(data) == 0:
            return
        print("Data:", data)
        data.replace("PING", "")
        if self.needsConfirmation:
            code = data[3:7]
            size = int(data[7:10])
            name = data[10:10+size]
            print(name)
            if code == "0000":
                print("Becoming a host!")
                self.becomeHost()
            else:
                print("Trying to find host", code)
                self.host = findHost(code)
                if self.host:
                    print("Found host.")
                    self.name = name
                    self.confirm()
                else:
                    print("No host found.")
        else:
            if self.host.socket:
                try:
                    self.host.socket.send(data)
                except:
                    self.host.disconnect()
                    print("Host's socket is closed.")

    # This is called to confirm to the client that they have been accepted,
    # after they send us their details.
    def confirm(self):
        self.needsConfirmation = False
        found = False
        for p in self.host.players:
            player = self.host.players[p]
            if (player.name == self.name):
                self.pID = player.pID
                found = True
                break;
        if (found != True):
            self.pID = self.host.getNextpID()
        print("Player ID is", self.pID)
        self.host.players[self.pID] = self
        self.sID = extend(self.pID, 2)
        html = "game.html"
        script = "script.js"
        self.socket.send("999" + self.sID + extend(len(html), 3) + html + extend(len(script), 3) + script)
        if (found != True):
            self.host.socket.send("998" + self.sID + extend(len(self.name), 3) + self.name)

    def becomeHost(self):
        host = Host(self.socket, newHostCode())
        clients.remove(self)
        hosts.append(host)

    def disconnect(self):
        print("Lost client...")
        clients.remove(self)
        self.socket = None
        return

class Host:
    
    def __init__(self, socket, hostCode):
        self.socket = socket
        self.hostCode = hostCode
        self.players = {}
        self.pID = 0
        self.socket.send("999" + str(self.hostCode))

        self.writingTo = 0

        self.data = ""

    def getNextpID(self):
        self.pID += 1
        return self.pID

    def handle(self):
        data = ""
        if (self.socket):
            try:
                raw = self.socket.readRaw()
                if raw == None:
                    return self.disconnect()
                else:
                    self.data += raw
            except:
                self.disconnect()
        if len(self.data) == 0:
            return
        print("Host says: "+self.data)
        self.data.replace("PING", "")
        ind = self.data.find("*")
        if (ind < 0):
            return
        if self.writingTo == 0:
            try:
                self.writingTo = int(self.data[0:2])
            except:
                self.data = self.data[1:]
                self.handle()
                return;
        pID = self.writingTo
        if self.players[pID]:
            if self.players[pID].socket:
                try:
                    self.players[pID].socket.send(self.data[2:ind])
                except:
                    self.players[pID].socket = None;
                    print("Client's socket closed.")
        else:
            print("Host", self.hostCode," tried to send a messaged to non-existant player", pID)
        self.data = self.data[ind+1:]
        self.writingTo = 0
        
    def disconnect(self):
        print("Lost host.")
        hosts.remove(self)
        self.socket = None
        return

def findHost(code):
    for host in hosts:
        if host.hostCode == code:
            return host
    return None

def newHostCode():
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    code = ''.join(chars[int(random.random()*26)] for _ in range(4))
    if findHost(code):
        return newHostCode()
    return code

def extend(v, l):
    out = str(v)
    while len(out) < l:
        out = "0" + out
    return out

# This handles a new client.
# We need to hand them to an object
# so that we can read and write from it
def handle(socket):
    global clients
    client = Client(socket)
    clients.append(client)

def main():
    print(sys.argv)
    global gameStarted
    global stage
    try:
        setupMessages()
        server = startServer()
        while True:
            newClient = handleNetwork()
            if newClient:
                handle(newClient)
            for client in clients:
                client.handle()
            for host in hosts:
                host.handle()
            sleep(0.01)
    except KeyboardInterrupt:
        print(' received, closing server.')
        server.close()
    
clients = []
hosts = []
pID = 0

if __name__ == '__main__':
    main()
