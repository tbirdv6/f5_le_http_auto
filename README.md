# f5_le_http_auto
Script to automatically update certificate and update an F5 client ssl profile. 

Pre Reqs
Python 2.7
pip
f5 python sdk
certbot

1. Create new cert.

create new cert using <code>certbot certonly --webroot -w /var/www/html/cert -d example.com -d test.example.com</code>

2. Edit Python script. 

Change the following lines to reflect your domain(s).

<code>domain = 'test.example.com'</code>
<code>key = '/etc/letsencrypt/live/example.com/privkey.pem'</code>
<code>cert = '/etc/letsencrypt/live/example.com/cert.pem'</code>
<code>chain = '/etc/letsencrypt/live/example.com/chain.pem'</code>

3. Edit the config/creds.json file to reflect you F5 Managment port and credentials. 

4. Cron
Add <code>certbot renew</code> to cron. (once a month should work)
Add the python script to cron running after the renew.

The bulk of the script came from Jason Rahm of F5 Networks. 
