#!/usr/bin/env python

from SimpleHTTPProxy import SimpleHTTPProxyHandler, test
import ssl
import os
import urlparse
import time
from subprocess import Popen, PIPE
from config import get_conf

INIT_CONFIG = {
    'hackUrl': {
        "test.com/path": "./test.json"
    }
}

config = get_conf(INIT_CONFIG)


class SSLBumpProxyHandler(SimpleHTTPProxyHandler):
    timeout = None  # FIXME: SSL connection to the client needs to be closed every time
    keyfile = 'SSLBumpProxy/server.key'
    certfile = 'SSLBumpProxy/server.crt'
    ca_keyfile = 'SSLBumpProxy/ca.key'
    ca_certfile = 'SSLBumpProxy/ca.crt'
    dynamic_certdir = 'SSLBumpProxy/dynamic/'  # set None if you use a static certificate

    if os.path.exists('/config'):
        keyfile = '/config/server.key'
        certfile = '/config/server.crt'
        ca_keyfile = '/config/ca.key'
        ca_certfile = '/config/ca.crt'
        dynamic_certdir = '/config/dynamic/'  # set None if you use a static certificate
        if not os.path.exists('/config/generate_certificates.sh'):
            os.system('cp SSLBumpProxy/generate_certificates.sh /config/generate_certificates.sh')
            if not os.path.exists('/config/ca.crt'):
                os.system('cd /config && sh ./generate_certificates.sh')

    def response_handler(self, req, reqbody, res, resbody):
        global config
        if config.get('hackUrl'):
            if req.path in config.get('hackUrl').keys():
                with open(config.get('hackUrl')[req.path], 'r') as f:
                    data = f.read()
                return data

    def request_handler(self, req, reqbody):
        if req.command == 'CONNECT':
            self.send_response(200, 'Connection Established')
            self.send_header('Connection', 'Keep-Alive')
            self.end_headers()

            if self.dynamic_certdir:
                if not os.path.isdir(self.dynamic_certdir):
                    os.makedirs(self.dynamic_certdir)

                u = urlparse.urlsplit(req.path)
                certpath = "%s/%s.crt" % (self.dynamic_certdir.rstrip('/'), u.hostname)
                with self.global_lock:
                    if not os.path.isfile(certpath):
                        epoch = "%d" % (time.time() * 1000)
                        p1 = Popen(["openssl", "req", "-new", "-key", self.keyfile, "-subj",
                                    "/CN=%s/O=SimpleHTTPProxy/OU=SimpleHTTPProxy/L=net" % u.hostname], stdout=PIPE)
                        p2 = Popen(["openssl", "x509", "-req", "-days", "3650", "-CA", self.ca_certfile, "-CAkey",
                                    self.ca_keyfile, "-set_serial", epoch, "-out", certpath], stdin=p1.stdout,
                                   stderr=PIPE)
                        p1.stdout.close()
                        p2.communicate()
                self.connection = ssl.wrap_socket(self.connection, keyfile=self.keyfile, certfile=certpath,
                                                  server_side=True)
            else:
                self.connection = ssl.wrap_socket(self.connection, keyfile=self.keyfile, certfile=self.certfile,
                                                  server_side=True)
            self.rfile = self.connection.makefile("rb", self.rbufsize)
            self.wfile = self.connection.makefile("wb", self.wbufsize)

            self.https_origin = req.path.rstrip('/')
            return True
        elif req.command == 'GET' and req.path == 'http://proxy.test/':
            with open(self.ca_certfile, 'rb') as f:
                data = f.read()

            self.send_response(200)
            self.send_header('Content-Type', 'application/x-x509-ca-cert')
            self.send_header('Content-Length', len(data))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(data)
            return True
        else:
            if hasattr(self, 'https_origin'):
                req.path = self.https_origin + req.path


if __name__ == '__main__':
    test(HandlerClass=SSLBumpProxyHandler)
