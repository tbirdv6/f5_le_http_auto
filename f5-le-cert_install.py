#!/usr/bin/python
import logging
import requests
import json
from f5.bigip import ManagementRoot
from f5.bigip.contexts import TransactionContextManager
import os
import sys
import time

requests.packages.urllib3.disable_warnings()

# slurp credentials
with open('config/creds.json', 'r') as f:
    config = json.load(f)
f.close()

f5_host = config['f5host']
f5_user = config['f5acct']
f5_password = config['f5pw']
domain = 'test.example.com'
key = '/etc/letsencrypt/live/example.com/privkey.pem'
cert = '/etc/letsencrypt/live/example.com/cert.pem'
chain = '/etc/letsencrypt/live/example.com/chain.pem'


mr = ManagementRoot(f5_host, f5_user, f5_password)

# Upload files
mr.shared.file_transfer.uploads.upload_file(key)
mr.shared.file_transfer.uploads.upload_file(cert)
mr.shared.file_transfer.uploads.upload_file(chain)

# Check to see if these already exist
key_status = mr.tm.sys.file.ssl_keys.ssl_key.exists(
    name='{0}.key'.format(domain))
cert_status = mr.tm.sys.file.ssl_certs.ssl_cert.exists(
    name='{0}.crt'.format(domain))
chain_status = mr.tm.sys.file.ssl_certs.ssl_cert.exists(name='le-chain.crt')

if key_status and cert_status and chain_status:

    # Because they exist, we will modify them in a transaction
    tx = mr.tm.transactions.transaction
    with TransactionContextManager(tx) as api:
        modkey = api.tm.sys.file.ssl_keys.ssl_key.load(
            name='{0}.key'.format(domain))
        modkey.sourcePath = 'file:/var/config/rest/downloads/{0}'.format(
            os.path.basename(key))
        modkey.update()

        modcert = api.tm.sys.file.ssl_certs.ssl_cert.load(
            name='{0}.crt'.format(domain))
        modcert.sourcePath = 'file:/var/config/rest/downloads/{0}'.format(
            os.path.basename(cert))
        modcert.update()

        modchain = api.tm.sys.file.ssl_certs.ssl_cert.load(
            name='le-chain.crt')
        modchain.sourcePath = 'file:/var/config/rest/downloads/{0}'.format(
            os.path.basename(chain))
        modchain.update()


else:
    newkey = mr.tm.sys.file.ssl_keys.ssl_key.create(
        name='{0}.key'.format(domain),
        sourcePath='file:/var/config/rest/downloads/{0}'.format(
            os.path.basename(key)))
    newcert = mr.tm.sys.file.ssl_certs.ssl_cert.create(
        name='{0}.crt'.format(domain),
        sourcePath='file:/var/config/rest/downloads/{0}'.format(
            os.path.basename(cert)))
    newchain = mr.tm.sys.file.ssl_certs.ssl_cert.create(
        name='le-chain.crt',
        sourcePath='file:/var/config/rest/downloads/{0}'.format(
            os.path.basename(chain)))

#Create SSL Profile if necessary
if not mr.tm.ltm.profile.client_ssls.client_ssl.exists(
        name='cssl.{0}'.format(domain), partition='Common'):
    cssl_profile = {
        'name': '/Common/cssl.{0}'.format(domain),
        'cert': '/Common/{0}.crt'.format(domain),
        'key': '/Common/{0}.key'.format(domain),
        'chain': '/Common/le-chain.crt',
        'defaultsFrom': '/Common/clientssl'
    }
    mr.tm.ltm.profile.client_ssls.client_ssl.create(**cssl_profile)


