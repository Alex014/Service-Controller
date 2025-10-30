# Service-Controller
Operations with SystemD services (Start/Stop)

# description
* Edit `services.json` file and write in your services
* Execute `sudo python run.py services.json`, the process will write the status of your services and execute commands on your services
* Edit `command` element (*start* or *stop*) in `services.json` file to start/stop your services
* Read the `status` and `log` elements
