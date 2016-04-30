#!/usr/bin/env python3

import requests
import channel

import argparse
import time

from secret import SHARED_SECRET
secret_part_prefix='server/secret.part'
nparts=20


def client_main(args):
  tunnel_data = dict(key=SHARED_SECRET,
                     endpoint_addr=(args.server, channel.SERVER_TUNNEL_PORT))
  host, stap = channel.create_client(tunnel_data)

  time.sleep(0.2)
  s = requests.Session()

  with open('/tmp/result_file', 'wb') as f:
    for i in range(nparts):
      res = s.get('http://%s/%s%02d' % (host, secret_part_prefix, i))
      f.write(res.content)
  stap()


def server_main(args):
  server_data = dict(key=SHARED_SECRET)
  stap=channel.create_server(server_data)
  return stap


def main():
  parser = argparse.ArgumentParser()
  sp = parser.add_subparsers()
  client_parser = sp.add_parser('client')
  client_parser.set_defaults(func=client_main)
  client_parser.add_argument('--server', type=str, default='localhost')

  server_parser = sp.add_parser('server')
  server_parser.set_defaults(func=server_main)

  args = parser.parse_args()
  args.func(args)


if __name__ == '__main__':
  main()
