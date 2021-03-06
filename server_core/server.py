#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from quarry.net.server import ServerFactory, ServerProtocol
from random import randint
import packet as p
import permissions as perms
import randomdata as dats
import commands as cmd
import json
from sys import exit as sysex
from server_core.chat import pushChat, pushChatCall

eobj_byid = {}
anim_i = 0

class Mineserver(ServerProtocol):
    plugins = ["Mineserver Core", "TotallyNotAPlugin", "example"]
    
    def packet_login_start(self, buff):
        if not options.down:
            ServerProtocol.packet_login_start(self, buff)
        else:
            buff.discard()
            self.close(options.downmsg)
    def player_joined(self):
        ServerProtocol.player_joined(self)

        self.ip = self.remote_addr.host
        self.eid = dats.getFreeId()
        self.fquid = self.username + "[/" + self.ip + "](" + str(self.uuid) + ")"
        self.base_scba_split = list("PyMINESERVER")
        self.anim_i = 0
        eobj_byid[self.eid] = self
        self.logger.info("UUID of player Dragon5232 is " + str(self.uuid))
        
        p.game(self, self.eid, 1, 0, 1, options.maxplayers, "default", False)
        p.spawn_pos(self, 0, 66, 0)
        p.abilities(self, True, True, True, True, 0.2, 0.2)
        p.pos_look(self, 0, 66, 0, 0, 0, False)
        p.rain(self, True)
        p.empty_chunk(self, 0, 0)
        p.block_change(self, 0, 64, 0, 1)
        if self.protocol_version == 47: p.plist_head_foot(self, u"§6P§2yMINESERVER§r", u"§eEnjoy the Test§r")
        if self.protocol_version == 47: self.tasks.add_loop(1.0/20, self.anim_frame_scb)
        relayPlayerList()
        self.logger.info(self.username + "[/" + self.ip + "] logged in with entity id " + str(self.eid) + " at ([nonexistent](0.0, 64.0, 0.0))")
        
        # Schedule 6-second sending of keep-alive packets.
        self.tasks.add_loop(6, self.keepalive_send)
        
        self.eobj_byid = eobj_byid
        pushChat(self, "\u00A7e" + self.username + " has joined the game\u00A7r", 1)
        
        # Send welcome title and subtitle
        p.title(self, options.wtitle)
        p.subtitle(self, options.wst)
        
        p.chat_json(self, dats.join_json(self), 1)
    def player_left(self):
        ServerProtocol.player_left(self)
        self.eobj_byid = eobj_byid
        pushChatCall(self, "\u00A7e" + self.username + " has left the game\u00A7r", 1, self.destroy)
    def keepalive_send(self):
        self.last_keepalive = random_digits(randint(4, 9))
        p.keep_alive(self, self.last_keepalive)
    def packet_keep_alive(self, buff):
        if buff.unpack_varint() == self.last_keepalive: pass
        else:
            if self.keepalive_miss < 4:
                self.keepalive_miss += 1
            else:
                buff.discard()
                self.logger.info("Kicking player " + self.username + " for not responding to keepalives for 24 seconds.")
                self.close("Timed out: did not ping for 24 seconds.")
    def packet_chat_message(self, buff):
        _atmp = buff.unpack_string()
        self.eobj_byid = eobj_byid
        cmd.handle(self, _atmp) if _atmp[0] == "/" else pushChat(self, "<" + self.username + "> " + _atmp.replace("\u00A7", ""), 0)
    def destroy(self):
        eobj_byid[self.eid] = None
    def nothing(self):
        random = "2random4me"
    def anim_frame_scb(self):
        self.sstmp = self.base_scba_split
        if self.anim_i >= len(self.sstmp): self.anim_i = 0
        self.sstmp[self.anim_i] = u"§6" + self.sstmp[anim_i] + u"§2"
        p.plist_head_foot(self, u"§2" + sstmp + u"§r", u"§eEnjoy the Test§r")
        anim_i += 1
    

class MineFactory(ServerFactory):
    protocol = Mineserver


def random_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def relayPlayerList():
    return None

def main(args):
    # Parse options
    import optparse
    parser = optparse.OptionParser(usage="usage: %prog [options]")
    parser.add_option("-a", "--host", dest="host", default="", help="address to listen on")
    parser.add_option("-p", "--port", dest="port", default="25565", type="int", help="port to listen on")
    parser.add_option("-m", "--motd", dest="motd", default="PyMineserver: Test. Hello! Now with joining! §b§l\\o/§r", type="string", help="motd to send to clients")
    parser.add_option("-o", "--offline", action="store_false", dest="auth", default=True, help="offline mode does not authenticate players!")
    parser.add_option("-k", "--downtime", action="store_true", dest="down", default=False, help="kick players with downtimemsg")
    parser.add_option("-q", "--downtimemsg", dest="downmsg", default="Sorry, but this server is currently down for maintenance. Check back soon!", help="message to kick for downtime with")
    parser.add_option("-w", "--wtitle", dest="wtitle", default="Welcome to Mineserver!", help="title to display on join")
    parser.add_option("-s", "--wsubtitle", dest="wst", default="Enjoy this test server!", help="subtitle to display on join")
    parser.add_option("-l", "--max-players", dest="maxplayers", default=20, help="max player count/limit")
    parser.add_option("-f", "--favicon", dest="favicon", default="creeper.png", help="relative path to server favicon in png")
    global options
    (options, args) = parser.parse_args(args)
    
    # Warn about auth mode
    if options.auth:
        print("Mineserver (warn/INFO)> Mineserver is running in online mode. All players must be authenticated to join. *(ONLINE)*")
    else:
        print("Mineserver (WARN/info)> Mineserver is running in offline mode. Players can join with fake UUIDs and names without authentication! *[OFFLINE]*!")

    # Create factory
    factory = MineFactory()
    factory.motd = options.motd
    factory.online_mode = options.auth
    factory.favicon = options.favicon

    # Listen
    factory.listen(options.host, options.port)
    factory.run()

if __name__ == "__main__":
    print("Mineserver (warn/CRIT)> You should NOT be invoking this directly! Use mineserver.py.")
    sysex(1)
