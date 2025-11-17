# Service-Controller
Operations with SystemD services and Bash commands (Start/Stop)

# Services
* Edit `services.json` file and write in your services
* Execute `sudo python run.py services.json commands.json`, the process will write the status of your services and execute commands on your services
* Edit `command` element (*start* or *stop*) in `services.json` file to start/stop your services
* Read the `status` and `log` elements

# Commands
* Edit `commands.json` file and write in your services
* Execute `sudo python run.py services.json commands.json`, the process will write the status of your services and execute commands on your services
* Change `status` element to *launch* in `commands.json` file to start your commands
* Read the `log` element
