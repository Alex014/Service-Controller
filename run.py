import json, os, sys, signal, time, subprocess
from pathlib import Path

class GLOBAL:
    halt = False
    services = ''

if len(sys.argv) < 2:
    print ("Usage: run.py <services.json>")
    exit(1)
else:
    GLOBAL.services = sys.argv[1]

if not os.path.exists(GLOBAL.services):
    print ("Services file '{}' does not exist".format(GLOBAL.services))
    exit(2)

def exit_fn (*args):
    GLOBAL.halt = True

signal.signal(signal.SIGINT, exit_fn)
signal.signal(signal.SIGTERM, exit_fn)

def update_config ():
    with open(GLOBAL.services, 'r') as file:
        keydata = json.loads(file.read())
        file.close()
        
    for service_name in keydata:
        result = subprocess.getoutput("systemctl is-active {}".format(service_name))

        if result == 'active':
            keydata[service_name]['status'] = 'running'
            keydata[service_name]['log'] = ''
        else:
            keydata[service_name]['status'] = 'stopped'

        result = subprocess.getoutput("systemctl is-failed {}".format(service_name))

        if result == 'failed':
            keydata[service_name]['status'] = 'failed'

    with open(GLOBAL.services, 'w') as file:
        file.write(json.dumps(keydata))
        file.close()

def execute_config ():
    with open(GLOBAL.services, 'r') as file:
        keydata = json.loads(file.read())
        file.close()
        
    for service_name in keydata:
        command = keydata[service_name]['command']

        if command == 'start':
            command = "systemctl start {}".format(service_name)
            keydata[service_name]['log'] = subprocess.getoutput(command)
            keydata[service_name]['command'] = ""
        elif command == 'restart':
            command = "systemctl restart {}".format(service_name)
            keydata[service_name]['log'] = subprocess.getoutput(command)
            keydata[service_name]['command'] = ""
        elif command == 'stop':
            command = "systemctl stop {}".format(service_name)
            keydata[service_name]['log'] = subprocess.getoutput(command)
            keydata[service_name]['command'] = ""

    with open(GLOBAL.services, 'w') as file:
        file.write(json.dumps(keydata))
        file.close()


while True:
    if GLOBAL.halt:
        break

    update_config()
    time.sleep(1)
    execute_config()
    time.sleep(1)