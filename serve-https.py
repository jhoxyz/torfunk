#!/usr/bin/env python3
"""Serve the planner over HTTPS on the local network.

Phones only let https pages hand images to other apps (WhatsApp), so plain
`python3 -m http.server` isn't enough to test sharing on a phone.

The first run creates a small local certificate authority (CA). Install its
certificate on the phone once (it is served at https://<laptop-ip>:<port>/ca.crt);
after that the phone trusts this server. If the laptop's IP changes, only the
server certificate is re-issued, so the phone keeps trusting it.

Usage: python3 serve-https.py [--port 8443]
"""
import argparse
import functools
import http.server
import socket
import ssl
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Outside the served folder, so the CA key can never be downloaded.
CERTS = Path.home() / '.local' / 'share' / 'formation-planner' / 'certs'
CA_KEY, CA_CRT = CERTS / 'ca.key', CERTS / 'ca.crt'
SERVER_KEY, SERVER_CRT, SERVER_IP = CERTS / 'server.key', CERTS / 'server.crt', CERTS / 'server.ip'


def lan_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('10.255.255.255', 1))  # sends nothing; just picks the network interface
        return s.getsockname()[0]


def openssl(*args):
    subprocess.run(['openssl', *args], check=True, capture_output=True)


def ensure_certs(ip):
    CERTS.mkdir(parents=True, exist_ok=True)
    if not CA_CRT.exists():
        print('Creating local certificate authority …', flush=True)
        openssl('req', '-x509', '-new', '-newkey', 'rsa:2048', '-nodes', '-days', '3650',
                '-keyout', str(CA_KEY), '-out', str(CA_CRT),
                '-subj', '/CN=Formation Planner local CA',
                '-addext', 'basicConstraints=critical,CA:TRUE',
                '-addext', 'keyUsage=critical,keyCertSign,cRLSign')
        CA_KEY.chmod(0o600)
    if SERVER_CRT.exists() and SERVER_IP.exists() and SERVER_IP.read_text() == ip:
        return
    print(f'Issuing server certificate for {ip} …', flush=True)
    csr, ext = CERTS / 'server.csr', CERTS / 'server.ext'
    ext.write_text(
        f'subjectAltName=IP:{ip},IP:127.0.0.1,DNS:localhost\n'
        'basicConstraints=CA:FALSE\n'
        'keyUsage=digitalSignature,keyEncipherment\n'
        'extendedKeyUsage=serverAuth\n')
    openssl('req', '-new', '-newkey', 'rsa:2048', '-nodes',
            '-keyout', str(SERVER_KEY), '-out', str(csr), '-subj', '/CN=formation-planner')
    # Apple rejects server certificates valid for more than 825 days; 397 is safe everywhere.
    openssl('x509', '-req', '-in', str(csr), '-CA', str(CA_CRT), '-CAkey', str(CA_KEY),
            '-CAcreateserial', '-days', '397', '-out', str(SERVER_CRT), '-extfile', str(ext))
    SERVER_KEY.chmod(0o600)
    SERVER_IP.write_text(ip)


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ca.crt':
            data = CA_CRT.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'application/x-x509-ca-cert')
            self.send_header('Content-Disposition', 'attachment; filename="formation-planner-ca.crt"')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--port', type=int, default=8443)
    port = parser.parse_args().port

    ip = lan_ip()
    ensure_certs(ip)
    httpd = http.server.ThreadingHTTPServer(('0.0.0.0', port), functools.partial(Handler, directory=str(ROOT)))
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(SERVER_CRT, SERVER_KEY)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

    print(f'''
Planner:         https://{ip}:{port}/
Phone, once:     open https://{ip}:{port}/ca.crt (accept the warning this one time),
                 install the certificate as a CA certificate, then reopen the planner.
Stop with Ctrl+C.
''', flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
