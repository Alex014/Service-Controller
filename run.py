import json, os, sys, signal, time, subprocess
from pathlib import Path
import datetime
from time import gmtime, strftime

class GLOBAL:
    halt = False
    services = '/home/privateness/services.json'
    commands = '/home/privateness/commands.json'

if not os.path.exists(GLOBAL.services):
    with open(GLOBAL.services, 'w+') as file:
        # data = {
        #     "mysql": { "status": "running", "command": "", "icon": "fas fa-user-shield", "style": "background: linear-gradient(135deg, var(--primary), #4895ef);", "log": "" },
        #     "tor": { "status": "running", "command": "", "icon": "fas fa-search", "style": "background: linear-gradient(135deg, var(--secondary), #3a0ca3);","log": "" },
        #     "cups": { "status": "running", "command": "", "icon": "fab fa-bitcoin", "style": "background: linear-gradient(135deg, #7209b7, #560bad);","log": "" },
        #     "ufw": { "status": "running", "command": "", "icon": "fas fa-network-wired", "style": "background: linear-gradient(135deg, #4cc9f0, var(--primary));","log": "" },
        #     "AmneziaVPN": { "status": "running", "command": "", "icon": "fas fa-file-upload", "style": "background: linear-gradient(135deg, var(--accent), #b5179e);","log": "" }
        # }
        data = {
            "ness": { "status": "running", "command": "", "icon": "fas fa-user-shield", "style": "background: linear-gradient(135deg, var(--primary), #4895ef);", "log": "" },
            "explorer": { "status": "running", "command": "", "icon": "fas fa-search", "style": "background: linear-gradient(135deg, var(--secondary), #3a0ca3);","log": "" },
            "emercoin": { "status": "running", "command": "", "icon": "fab fa-bitcoin", "style": "background: linear-gradient(135deg, #7209b7, #560bad);","log": "" },
            "ipfs": { "status": "running", "command": "", "icon": "fas fa-network-wired", "style": "background: linear-gradient(135deg, #4cc9f0, var(--primary));","log": "" },
            "vsftpd": { "status": "running", "command": "", "icon": "fas fa-file-upload", "style": "background: linear-gradient(135deg, var(--accent), #b5179e);","log": "" }
        }

        file.write(json.dumps(data))
        file.close()

    Path(GLOBAL.services).chmod(0o666)

if not os.path.exists(GLOBAL.commands):
    with open(GLOBAL.commands, 'w+') as file:

        data = {
            "source": {
                "param": "", 
                "status": "iddle", 
                "date": "", 
                "log": ""
            },
            "sysupgrade": {
                "param": "",
                "status": "iddle", 
                "date": "", 
                "log": ""
            },
            "cert": {
                "param": "", 
                "status": "iddle", 
                "date": "", 
                "log": ""
            },
            "userpass": {
                "param": "", 
                "status": "iddle", 
                "date": "", 
                "log": ""
            },
            "rootpass": {
                "param": "", 
                "status": "iddle", 
                "date": "", 
                "log": ""
            }
        }

        file.write(json.dumps(data))
        file.close()

    Path(GLOBAL.commands).chmod(0o666)
    

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

def run_commands ():
    def read_commands ():
        with open(GLOBAL.commands, 'r') as file:
            commands = json.loads(file.read())
            file.close()
            return commands

    def write_commands (commands):
        with open(GLOBAL.commands, 'w') as file:
            file.write(json.dumps(commands))
            file.close()

    commands = read_commands ()

    run = False
        
    for command in commands:
        if commands[command]['status'] == 'launch':
            commands[command]['status'] = 'running'

            if command == 'sysupgrade':
                run = 'apt update && apt -y upgrade'
                # run = 'ls -lh /home/privateness'
            elif command == 'cert':
                run = 'openssl req -x509 -newkey rsa:4096 -sha512 -keyout key.pem -out cert.pem -days 3650 -noenc -subj \"/C=VD/ST=VOID/L=VOID/O=VOID/OU=VOID/CN=VOID\" && cp cert.pem /usr/local/share/ca-certificates/cert.pem && cp key.pem /usr/local/share/ca-certificates/key.pem && systemctl restart apache2'
                # run = 'ls -lh /home/privateness'
            elif command == 'userpass':
                run = 'usermod --password privateness "{}"'.format(commands[command]['param']) + " && "  + \
                    "echo 'AuthType Basic' > .htaccess && echo 'AuthName \"Privateness password (default privateness)\" ' >> .htaccess && echo 'AuthUserFile /home/privateness/.htpasswd ' >> .htaccess && echo 'require valid-user' >> .htaccess && htpasswd -cb /home/privateness/.htpasswd privateness {}".format(commands[command]['param'])
                # run = "echo 'AuthType Basic' > .htaccess && echo 'AuthName \"Privateness password (default privateness)\" ' >> .htaccess && echo 'AuthUserFile /home/privateness/.htpasswd ' >> .htaccess && echo 'require valid-user' >> .htaccess && htpasswd -cb /home/privateness/.htpasswd privateness {}".format(commands[command]['param'])
            elif command == 'rootpass':
                run = 'usermod --password root "{}"'.format(commands[command]['param'])
                # run = 'ls -lh /home/privateness'
            elif command == 'source':
                run = 'cd /var/www && git pull origin master'
                # run = 'ls -lh /home/privateness'

            if run != False:
                commands[command]['log'] = subprocess.getoutput(run)
                commands[command]['date'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                commands[command]['status'] = 'done'
            else:
                commands[command]['status'] = 'iddle'

            # commands[command]['param'] = ''

            write_commands (commands)
            break

while True:
    if GLOBAL.halt:
        print ("\nexit")
        exit (0)

    execute_config()
    update_config()
    time.sleep(1)
    run_commands()
    time.sleep(1)

#AuthType Basic   
#AuthName "Privateness password (default privateness)" 
#AuthUserFile  .htpasswd
#require valid-user    

# echo 'AuthType Basic' > .htaccess && echo 'AuthName "Privateness password (default privateness)" ' >> .htaccess && echo 'AuthUserFile /home/privateness/.htpasswd ' >> .htaccess && echo 'require valid-user' >> .htaccess && htpasswd -cb /home/privateness/.htpasswd privateness privateness