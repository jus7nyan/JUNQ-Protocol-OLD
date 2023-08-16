import asyncio
import json

import log
"""

commands:
    register:
        if you want to have an identifier and the ability to sign messages,
        then you must register in the entry-point.
        but it is not required and you can skip this step
    auth:
        

"""
class Handler:
    
    def __init__(self):
        self.db = {
            "clients": {},
            "groups": {},
            "group signs": {},
            "signatures": {},
            "entry-points": []
        }
        self.version = "0.1.0"

        self.commands = {
            "0": self.register,
            "1": self.get_signature,
            "2": self.get_groups,
            "3": self.get_entry_points,
            "4": self.add_entry_points,
            "5": self.add_group,
            "6": self.get_client,
            "7": self.get_version,
            "256": self.is_entry_point
            }

        self.logger = log.Logger()
    
    async def register(self, addr ,reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        self.logger.info(f"register cmd from addr={addr}")
        writer.write(b"REGISTER")
        await writer.drain()
        data = await reader.read(1024)
        ident = data.decode()[:-1]
        if ident not in self.db["clients"].keys():
            data = await reader.read(4096)
            if data != b'':
                gpg_key = data.decode()[:-1]
                self.db["signatures"].update({ident:gpg_key})
                self.db["clients"].update({ident:addr})
                self.logger.info(f"succses registered {ident}:::{addr}:::{gpg_key}")
                writer.write(b"OK")
                await writer.drain()
        else:
            self.logger.debug(f"Allready reggistered id={ident}")
            writer.write(b"ALLREADY")
            await writer.drain()

    
    
    async def get_signature(self,addr, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        self.logger.info(f"get sign cmd from addr={addr}")
        writer.write(b"GET_SIGNATURE")
        await writer.drain()
        data = await reader.read(1024)
        ident = data.decode()[:-1]
        if ident[:3] == "usr":
            if ident[3:] in self.db["signatures"].keys():
                self.logger.info(f"requested sign for id={ident}")
                writer.write(self.db["signatures"][ident].encode())
                await writer.drain()
            else:
                    self.logger.debug(f"Wrong ident id={ident}")
                    writer.write(b"WRONG_IDENT")
                    await writer.drain()
        elif ident[:3] == "grp":
            if ident[3:] in self.db["groups signs"].keys():
                self.logger.info(f"requested sign for id={ident}")
                writer.write(self.db["goup signs"][ident].encode())
                await writer.drain()
            else:
                self.logger.debug(f"Wrong ident id={ident}")
                writer.write(b"WRONG_IDENT")
                await writer.drain()

    async def get_groups(self,addr, _, writer:asyncio.StreamWriter):
        self.logger.info(f"get groups cmd from addr={addr}")
        writer.write(str(self.db["groups"]).encode())
        await writer.drain()

    async def get_client(self, addr, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        self.logger.info(f"get client cmd from addr={addr}")
        writer.write(b"GET_CLIENT")
        await writer.drain()
        data = await reader.read(1024)
        ident = data.decode()[:-1]

        if ident in self.db["clients"].keys():
            writer.write(str({ "id":ident, "addr":self.db["clients"][ident], "sign":self.db["signatures"][ident] }).encode())
        else:
            self.logger.debug(f"Wrong ident id={ident}")
            writer.write(b"WRONG_IDENT")
            await writer.drain()

    async def add_group(self, addr, reader:asyncio.StreamReader, writer:asyncio.StreamWriter): 
        self.logger.info(f"add group cmd from addr={addr}")
        writer.write(b"ADD_ENTRY_P")
        await writer.drain()
        data = await reader.read(1024)
        group_name = data.decode()[:-1]
        if group_name not in self.db["groups"].keys():
            data = await reader.read(4096)
            gpg_key = data.decode()[:-1]
            data = await reader.read(256)
            save_server = data.decode()[:-1]
            data = await reader.read(1024)
            options = data.decode()[:-1]
            self.db["groups"].update({group_name:{"gpg-key":gpg_key,"save-server":save_server, "options":options}})
            self.db["group signs"].update({group_name:gpg_key})
            writer.write(b"OK")
            await writer.drain()
        else:
            self.logger.debug(f"Wrong group name id={group_name}")
            writer.write(b"WRONG_GR_NAME")
            await writer.drain()
    
    async def get_entry_points(self, addr, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        self.logger.info(f"get entry-points cmd from addr={addr}")
        writer.write(str(self.db["entry-points"]).encode())
        await writer.drain()
    async def add_entry_points(self, addr, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        self.logger.info(f"add group cmd from addr={addr}")
        writer.write(b"ADD_ENTRY_P")
        await writer.drain()
        data = await reader.read(1024)
        entry_point = data.decode()[:-1]
        if entry_point not in self.db["entry-points"]:
            self.db["entry-points"].append(entry_point)
            writer.write(b"OK")
            await writer.drain()
        else:
            self.logger.debug(f"Allready save entripoint ep={entry_point}")
            writer.write(b"ALLREADY")
            await writer.drain()

    async def get_version(self, addr, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        writer.write(self.version.encode())
        await writer.drain()
    
    async def is_entry_point(self, addr, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        writer.write(b"OK")
        await writer.drain()

    async def handle(self, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')[0]
        self.logger.info(f"client connect from addr={addr}")
        data = await reader.read(8)
        while data != b'':
            cmd = data.decode()[:-1]
            try:
                await self.commands[cmd](addr, reader, writer)
            except:
                self.logger.err(f"Wrong cmd={cmd}")
                writer.write(b"WRONG_CMD")
            data = await reader.read(8)
        self.logger.info(f"close connection from addr={addr}")
        writer.close()

    def end(self):
        json.dump(self.db, open("db.save.json", "w+"))
