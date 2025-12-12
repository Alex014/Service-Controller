import json, os, sys, signal, time, subprocess
from pathlib import Path
import datetime
from time import gmtime, strftime
import glob


class GLOBAL:
    halt = False
    path = "/home/privateness"
    services = path + "/services.json"
    commands = path + "/commands.json"
    self_update_file = path + "/.update"


if not os.path.exists(GLOBAL.services):
    with open(GLOBAL.services, "w+") as file:
        # data = {
        #     "mysql": { "status": "running", "command": "", "icon": "fas fa-user-shield", "style": "background: linear-gradient(135deg, var(--primary), #4895ef);", "log": "" },
        #     "tor": { "status": "running", "command": "", "icon": "fas fa-search", "style": "background: linear-gradient(135deg, var(--secondary), #3a0ca3);","log": "" },
        #     "cups": { "status": "running", "command": "", "icon": "fab fa-bitcoin", "style": "background: linear-gradient(135deg, #7209b7, #560bad);","log": "" },
        #     "ufw": { "status": "running", "command": "", "icon": "fas fa-network-wired", "style": "background: linear-gradient(135deg, #4cc9f0, var(--primary));","log": "" },
        #     "AmneziaVPN": { "status": "running", "command": "", "icon": "fas fa-file-upload", "style": "background: linear-gradient(135deg, var(--accent), #b5179e);","log": "" }
        # }
        data = {
            "ness": {
                "status": "running",
                "command": "",
                "icon": "fas fa-user-shield",
                "style": "background: linear-gradient(135deg, var(--primary), #4895ef);",
                "log": "",
            },
            "explorer": {
                "status": "running",
                "command": "",
                "icon": "fas fa-search",
                "style": "background: linear-gradient(135deg, var(--secondary), #3a0ca3);",
                "log": "",
            },
            "emercoin": {
                "status": "running",
                "command": "",
                "icon": "fab fa-bitcoin",
                "style": "background: linear-gradient(135deg, #7209b7, #560bad);",
                "log": "",
            },
            "ipfs": {
                "status": "running",
                "command": "",
                "icon": "fas fa-network-wired",
                "style": "background: linear-gradient(135deg, #4cc9f0, var(--primary));",
                "log": "",
            },
            "vsftpd": {
                "status": "running",
                "command": "",
                "icon": "fas fa-file-upload",
                "style": "background: linear-gradient(135deg, var(--accent), #b5179e);",
                "log": "",
            },
        }

        file.write(json.dumps(data))
        file.close()

    Path(GLOBAL.services).chmod(0o666)

if not os.path.exists(GLOBAL.commands):
    with open(GLOBAL.commands, "w+") as file:

        data = {
            "source": {"param": "", "status": "iddle", "date": "", "log": ""},
            "sysupgrade": {"param": "", "status": "iddle", "date": "", "log": ""},
            "cert": {"param": "", "status": "iddle", "date": "", "log": ""},
            "backup": {"param": "", "status": "iddle", "date": "", "last": False, "log": ""},
            "restore": {"param": "", "status": "iddle", "date": "", "last": False, "log": ""},
            "userpass": {"param": "", "status": "iddle", "date": "", "log": ""},
            "rootpass": {"param": "", "status": "iddle", "date": "", "log": ""},
        }

        file.write(json.dumps(data))
        file.close()

    Path(GLOBAL.commands).chmod(0o666)


def exit_fn(*args):
    GLOBAL.halt = True


def is_self_upgrade():
    return os.path.exists(GLOBAL.self_update_file)


def begin_self_upgrade():
    return open(GLOBAL.self_update_file, 'a').close()
    # return subprocess.run('touch "{}"'.format(GLOBAL.self_update_file))


def end_self_upgrade():
    return os.remove(GLOBAL.self_update_file)


def get_last_backup():
    files = glob.glob(GLOBAL.path + "/Backup/*.tar.gz")
    files.sort(reverse=True)

    if len(files) > 0:
        return os.path.basename(files[0])
    else:
        return False


def get_last_restore():
    files = glob.glob(GLOBAL.path + "/Restore/*.tar.gz")
    files.sort(reverse=True)

    if len(files) > 0:
        return os.path.basename(files[0])
    else:
        return False


signal.signal(signal.SIGINT, exit_fn)
signal.signal(signal.SIGTERM, exit_fn)


def update_config():
    with open(GLOBAL.services, "r") as file:
        keydata = json.loads(file.read())
        file.close()

    for service_name in keydata:
        result = subprocess.getoutput("systemctl is-active {}".format(service_name))

        if result == "active":
            keydata[service_name]["status"] = "running"
            keydata[service_name]["log"] = ""
        else:
            keydata[service_name]["status"] = "stopped"

        result = subprocess.getoutput("systemctl is-failed {}".format(service_name))

        if result == "failed":
            keydata[service_name]["status"] = "failed"

    with open(GLOBAL.services, "w") as file:
        file.write(json.dumps(keydata))
        file.close()


def execute_config():
    with open(GLOBAL.services, "r") as file:
        keydata = json.loads(file.read())
        file.close()

    for service_name in keydata:
        command = keydata[service_name]["command"]

        if command == "start":
            command = "systemctl start {}".format(service_name)
            keydata[service_name]["log"] = subprocess.getoutput(command)
            keydata[service_name]["command"] = ""
        elif command == "restart":
            command = "systemctl restart {}".format(service_name)
            keydata[service_name]["log"] = subprocess.getoutput(command)
            keydata[service_name]["command"] = ""
        elif command == "stop":
            command = "systemctl stop {}".format(service_name)
            keydata[service_name]["log"] = subprocess.getoutput(command)
            keydata[service_name]["command"] = ""

    with open(GLOBAL.services, "w") as file:
        file.write(json.dumps(keydata))
        file.close()

def read_commands():
    with open(GLOBAL.commands, "r") as file:
        commands = json.loads(file.read())
        file.close()
        return commands

def write_commands(commands):
    with open(GLOBAL.commands, "w") as file:
        file.write(json.dumps(commands))
        file.close()

def update_commands():
    commands = read_commands()

    if not 'backup' in commands:
        commands['backup'] = {"param": "", "status": "iddle", "date": "", "last": False, "log": ""}

    if not 'restore' in commands:
        commands['restore'] = {"param": "", "status": "iddle", "date": "", "last": False, "log": ""}

    commands['backup']['last'] = get_last_backup()
    commands['restore']['last'] = get_last_restore()

    write_commands(commands)

def run_commands():
    commands = read_commands()

    run = False
    upgrade = False

    for command in commands:
        if commands[command]["status"] == "launch":
            commands[command]["status"] = "running"

            if command == "sysupgrade":
                run = "apt update && apt -y upgrade"
                upgrade = True
            elif command == "cert":
                run = 'openssl req -x509 -newkey rsa:4096 -sha512 -keyout key.pem -out cert.pem -days 3650 -noenc -subj "/C=VD/ST=VOID/L=VOID/O=VOID/OU=VOID/CN=VOID" && cp cert.pem /usr/local/share/ca-certificates/cert.pem && cp key.pem /usr/local/share/ca-certificates/key.pem && systemctl restart apache2'
                # run = 'ls -lh /home/privateness'
            elif command == "userpass":
                run = (
                    'PASS=$(echo "{}" | mkpasswd -s) && '.format(
                        commands[command]["param"]
                    )
                    + 'usermod --password "${PASS}" privateness'
                    + " && "
                    + "echo 'AuthType Basic' > .htaccess && echo 'AuthName \"Privateness password (default privateness)\" ' >> .htaccess && echo 'AuthUserFile {path}/.htpasswd ' >> .htaccess && echo 'require valid-user' >> .htaccess && htpasswd -cb {path}/.htpasswd privateness {passw}".format(
                        path = GLOBAL.path, passw = commands[command]["param"]
                    )
                )
                # run = "echo 'AuthType Basic' > .htaccess && echo 'AuthName \"Privateness password (default privateness)\" ' >> .htaccess && echo 'AuthUserFile /home/privateness/.htpasswd ' >> .htaccess && echo 'require valid-user' >> .htaccess && htpasswd -cb /home/privateness/.htpasswd privateness {}".format(commands[command]['param'])
            elif command == "rootpass":
                run = (
                    'PASS=$(echo "{}" | mkpasswd -s) && '.format(
                        commands[command]["param"]
                    )
                    + 'usermod --password "${PASS}" root'
                )
                # run = 'ls -lh /home/privateness'
            elif command == "source":
                run = "cd /var/www && git pull origin master"
                # run = 'ls -lh /home/privateness'
            elif command == "backup":
                run = 'dt=$(date +"%Y-%m-%d %T") && tar czf "{path}/Backup/{dt}-backup.tar.gz" {path}/.privateness/wallets {path}/.emercoin/wallets'.format(path = GLOBAL.path, dt = '${dt}')
            elif command == "restore":
                arc = get_last_restore()
                arc = arc.replace("/..", "")
                arc = arc.replace("/", "")
                run = 'systemctl stop emercoin && systemctl stop ness && systemctl stop explorer && '
                run += 'tar xzf "{path}/Restore/{arc}" -C / && rm -f "{path}/Restore/{arc}"'.format(path = GLOBAL.path, arc = arc)
                run += '&& systemctl start emercoin && systemctl start ness && systemctl start explorer'
            if run != False:
                commands[command]["log"] = subprocess.getoutput(run)
                commands[command]["date"] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                commands[command]["status"] = "done"
                # commands[command]["status"] = "iddle"
                
            if command == 'backup': 
                commands['backup']['last'] = get_last_backup()
            elif command == 'restore': 
                commands['restore']['last'] = get_last_restore()

            # commands[command]['param'] = ''

    write_commands(commands)

    if upgrade:
        print("\nWait for Service Controller upgrade ...")
        begin_self_upgrade()
        exit(0)


while True:
    if GLOBAL.halt:
        print("\nexit")
        exit(0)

    execute_config()
    update_config()
    time.sleep(1)
    run_commands()
    update_commands()

    if is_self_upgrade():
        print("\nUpgrading right now !")
        print("\nexit")
        exit(1)

    time.sleep(1)
