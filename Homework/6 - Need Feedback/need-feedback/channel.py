import io

import http.server
import socketserver
import threading
import select
import socket
import struct
import hashlib
import binascii
import random
import time
import traceback as tb
import os

from enum import IntEnum

SERVER_PORT = 1234
CLIENT_TUNNEL_PORT = 2345
SERVER_TUNNEL_PORT = 2346


class Sbox:

  def __init__(self, tb, nbit_out):
    self.tb = tb
    self.nbit_out = nbit_out
    self.nbit_in=0

    assert (len(self.tb)&(len(self.tb)-1))==0, 'not a power of 2'
    while len(self.tb)>>self.nbit_in!=1:
      self.nbit_in+=1


  def get(self, a):
    return self.tb[a]


class LFSR:

  def __init__(self, coeffs, n, state=1):
    poly = 0
    for j in coeffs:
      poly |= 1 << j
    self.coeffs = coeffs
    self.poly = poly
    self.n = n
    self.state = state

  def next(self):
    b = self.state >> (self.n - 1)
    self.state = self.state << 1
    assert b == 0 or b == 1
    if b:
      self.state ^= self.poly
    return b


class MultiLFSR:

  def __init__(self, lfsrs, sbox):
    self.lfsrs = lfsrs
    self.sbox = sbox
    self.q = []

  def next(self):
    if len(self.q) == 0:
      v = 0
      for j in range(self.sbox.nbit_in):
        u=0
        for lfsr in self.lfsrs:
          u ^= lfsr.next()
        v|=u<<j
      v = self.sbox.get(v)
      for i in range(self.sbox.nbit_out):
        self.q.append(v >> i & 1)

    res = self.q[0]
    self.q = self.q[1:]
    return res

  def seed(self, key, iv):
    need_bits = 0
    for lfsr in self.lfsrs:
      need_bits += lfsr.n

    cur = '{}#{}'.format(key, iv).encode()
    rand_bytes = b''
    while len(rand_bytes) * 8 < need_bits:
      cur = hashlib.sha256(cur+str(need_bits).encode()).digest()
      rand_bytes += cur

    num = int(binascii.hexlify(rand_bytes), 16)
    for lfsr in self.lfsrs:
      want = lfsr.n
      lfsr.state = num % (2**want)
      num >>= want

  def get_key(self):
    key = []
    for lfsr in self.lfsrs:
      for j in range(lfsr.n):
        key.append(lfsr.state >> j & 1)
    return ''.join([str(x) for x in key])


class KappaCrypto:

  def __init__(self, key):
    self.key = key
    self.count = 0
    sbox_tb = [ 7, 6, 5, 10, 8, 1, 12, 13, 6, 11, 15, 11, 1, 6, 2, 7, 0, 2,
                    8, 12, 3, 2, 15, 0, 1, 15, 9, 7, 13, 6, 7, 5, 9, 11, 3, 3,
                    12, 12, 5, 10, 14, 14, 1, 4, 13, 3, 5, 10, 4, 9, 11, 15, 10,
                    14, 8, 13, 14, 2, 4, 0, 0, 4, 9, 8,]
    lfsr_coeffs = [
[0x0 ,0x1 ,0x2 ,0x3 ,0x6 ,0x9 ,0xa],
[0x0 ,0x1 ,0x2 ,0x3 ,0x6 ,0x7 ,0x9 ,0xa ,0xb],
[0x0 ,0x2 ,0x7 ,0x8 ,0xa ,0xb ,0xc],
[0x0 ,0x1 ,0x3 ,0x7 ,0xa ,0xb ,0xd],
[0x0 ,0x3 ,0x4 ,0xa ,0xb ,0xc ,0xe],
    ]

    sbox = Sbox(sbox_tb, 4)
    lfsrs = []
    for coeffs in lfsr_coeffs:
      lfsr = LFSR(coeffs, coeffs[-1])
      lfsrs.append(lfsr)

    self.mlfsr = MultiLFSR(lfsrs, sbox)
    self.key = key
    self.iv = 0
    self.reseed()

  def reseed(self):
    self.iv += 1
    self.mlfsr.seed(self.key, self.iv)


  # symmetric
  def proc(self, msg, is_enc):
    self.count += len(msg)

    msg2 = bytearray(msg)
    for i in range(len(msg2)):
      for k in range(8):
        msg2[i] ^= self.mlfsr.next() << k
    return msg2
    #return bytes([a ^ 72 for a in msg])


class NoCrypto:

  def proc(self, msg, is_enc):
    return msg


class KappaPacket:

  def __init__(self):
    self.msg = b''

  def append(self, a):
    self.msg += a

  def get_msg_len(self):
    return struct.unpack('<I', self.msg[:4])[0]

  def has_full(self):
    if len(self.msg) < 4:
      return False

    return self.get_msg_len() + 4 <= len(self.msg)

  def extract_one(self):
    if not self.has_full():
      return None

    cur_len = self.get_msg_len()
    res = self.msg[4:4 + cur_len]
    self.msg = self.msg[4 + cur_len:]
    return KappaMsg.Deserialize(res)

  def Make(content):
    return struct.pack('<I', len(content)) + content


class MsgType(IntEnum):
  reseed = 1
  data = 2


class KappaMsg:

  def __init__(self, typ, **kwargs):
    self.typ = typ
    self.__dict__.update(kwargs)

  def serialize(self):
    buf = struct.pack('<I', self.typ)
    if self.typ == MsgType.reseed:
      buf += self.iv
    elif self.typ == MsgType.data:
      buf += self.data
    else:
      assert 0
    return buf

  def Deserialize(msg):
    assert len(msg) >= 4
    typ = struct.unpack('<I', msg[:4])[0]
    if typ == MsgType.reseed:
      return KappaMsg(typ=MsgType.reseed, iv=msg[4:])
    elif typ == MsgType.data:
      return KappaMsg(typ=MsgType.data, data=msg[4:])
    else:
      assert 0


class KappaChannel:

  def __init__(self, key, s_tunnel=None, s_service=None, is_server=False):
    self.key = key
    self.s_tunnel = s_tunnel
    self.s_service = s_service
    self.buffered_send = b''
    self.is_server = is_server
    if is_server:
      self.send_cr = KappaCrypto(key)
      self.recv_cr = NoCrypto()
    else:
      self.send_cr = NoCrypto()
      self.recv_cr = KappaCrypto(key)
    self.from_server=open('/tmp/from_service{}'.format(is_server), 'wb')

    self.msg = KappaPacket()

  def send_tunnel(self, msg):
    data = KappaPacket.Make(msg)
    self.s_tunnel.send(data)

  def tunnel(self):
    buf = self.s_tunnel.recv(1024)
    if not buf:
      return False
    self.msg.append(buf)
    while True:
      e = self.msg.extract_one()
      if not e:
        break
      if e.typ == MsgType.data:
        self.proc_data(e)
      elif e.typ == MsgType.reseed:
        self.proc_reseed(e)
      else:
        assert 0
    return True

  def service(self):
    buf = self.s_service.recv(2048)
    # end of connection
    if len(buf) == 0:
      return False
    self.from_server.write(buf)
    self.from_server.flush()
    data = self.send_cr.proc(buf, True)
    msg = KappaMsg(typ=MsgType.data, data=data)
    self.send_tunnel(msg.serialize())
    return True

  def proc(self):
    while True:
      rd, _, _ = select.select([self.s_service, self.s_tunnel], [], [])
      if self.s_tunnel in rd:
        if not self.tunnel():
          break

      if self.s_service in rd:
        if not self.service():
          break
    self.close()

  def close(self):
    self.s_tunnel.close()
    self.s_service.close()

  def proc_data(self, e):
    res = self.recv_cr.proc(e.data, False)
    self.s_service.send(res)

  def proc_reseed(self, e):
    assert 0, "unimplemented"
    pass


class KappaTunnelHandler:

  def __init__(self, endpoint_addr=None, key=None, server=False):
    assert endpoint_addr and key
    self.endpoint_addr = endpoint_addr
    self.key = key
    self.is_server = server

    self.channels = {}

  def __call__(self, cur_sock, client_addr, _):

    sock_x = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_x.connect(self.endpoint_addr)

    if self.is_server:
      s_service = sock_x
      s_tunnel = cur_sock
    else:
      s_tunnel = sock_x
      s_service = cur_sock
    if client_addr[0] in self.channels:
      channel = self.channels[client_addr[0]]
      channel.s_service = s_service
      channel.s_tunnel = s_tunnel
      channel.proc()
      return

    channel = KappaChannel(self.key,
                           s_service=s_service,
                           s_tunnel=s_tunnel,
                           is_server=self.is_server)
    channel.proc()
    self.channels[client_addr[0]] = channel


def stop_servers_func(servers):

  def stop_servers():
    for x in servers:
      print('shutdown', x)
      x.shutdown()
      print('done', x)

  return stop_servers


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
  pass


def create_server(server_data):
  tunnel_host = ('', SERVER_TUNNEL_PORT)
  httpd_host = ('localhost', SERVER_PORT)

  server = ThreadedTCPServer(tunnel_host,
                                  KappaTunnelHandler(server=True,
                                                     endpoint_addr=httpd_host,
                                                     **server_data), bind_and_activate=False)
  server.allow_reuse_address = True
  server.server_bind()
  server.server_activate()
  threading.Thread(target=server.serve_forever).start()

  Handler = http.server.SimpleHTTPRequestHandler
  httpd = ThreadedTCPServer(("localhost", SERVER_PORT), Handler, bind_and_activate=False)
  httpd.allow_reuse_address = True
  httpd.server_bind()
  httpd.server_activate()
  threading.Thread(target=httpd.serve_forever).start()
  return stop_servers_func([server, httpd])


def create_client(tunnel_data):
  host = ('localhost', CLIENT_TUNNEL_PORT)

  server = ThreadedTCPServer(host, KappaTunnelHandler(**tunnel_data), bind_and_activate=False)
  server.allow_reuse_address = True
  server.server_bind()
  server.server_activate()
  threading.Thread(target=server.serve_forever).start()
  return '%s:%d' % host, stop_servers_func([server])
