import asyncio
import json

import log

class Handler:
    def __init__(self, db_path) -> None:
        self.version = "0.1.0"
        self.db_path = db_path
        self.logger = log.Logger()

        self.memory_db = {
            "clients": {}, # {nickname:{"gpg": gpg-key,"addr": address}}
            "groups": {}, # {name:{"gpg": gpg-key,"creator":creator info,"users":[user's info list]}}
            "entry points": {} # {name:{"addr": address,"gpg": gpg-key}}
        }
        
        self.cmds = {
            "register": self.register , # register gpg key, nickname, addr in entry point
            "get version": ... , # get entry point protocol version
            "get gpg key": ... , # get gpg public key of user, group or entry point
            "get groups": ... , # get groups list (group_name, group creator info, information about participants) ## maybe type of group
            "get entry points": ... , # get known entry points  |----> for load distribution and new information load
            "add entry points": ... , # add user's entry points |-^
            "register group": ... , # register created group
            "get client info": ..., # get info about user by nickname
            "update address": ... , # update address if you lost old address but have old gpg key. for save nickname

        }
        self.exceptions = {
            "bad command": {"error": "bad command"},
        }
        self.messages = {
            "OK": {"message": "OK"},
        }

    async def register(self, address, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, cargs: dict):
        """
        for register you need choose unic nickname, gpg public key
        """
        self.logger.info(f"user register command from {address}")
        self.memory_db["clients"].update({cargs["nick"]:{"gpg":cargs["gpg"],"addr":address}})
        msg = json.dumps(self.messages["OK"])
        writer.write(msg.encode())
        await writer.drain()
        self.logger.info(f"user registered {address}:{cargs['nick']}:{cargs['gpg']}")
        ...

    async def handle(self, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        print(self.memory_db.__sizeof__())
        address = writer.get_extra_info('peername')[0]
        self.logger.info(f"client connect from addr={address}")


        data = await reader.read(4096)
        while data != b'':
            cmd = data.decode()
            try:
                cmd = json.loads(cmd)
                for i in cmd:
                    comand = i[0]
                    cargs = i[1]
                    await self.cmds[comand](address, reader, writer, cargs) # message must looks like [[command,args],...]
            
            except:
                self.logger.err(f"Wrong cmd={cmd}")
                await self.__send_exception("bad command", writer)
                
            data = await reader.read(4096)
        self.logger.info(f"close connection from addr={address}")
        writer.close()


        ...
    async def __send_exception(self, exception, writer: asyncio.StreamWriter):
        msg = json.dumps(self.exceptions[exception])
        writer.write(msg.encode())
        await writer.drain()

    def end(self): ... 
