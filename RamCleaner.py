from configparser import ConfigParser
from time import sleep

import requests as req

config = ConfigParser()
config.read("config.ini")

memory_treshold = int(config["General"]["MemoryTreshold"]) * 1000000

server_identifier = config["General"]["ServerIdentifierShort"]
request_base_url = config["General"]["PanelURL"] + \
    "/api/client/servers/" + server_identifier
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + config["General"]["APIKey"]
}
wait_time = 60

while True:
    response = req.get(request_base_url + "/resources",
                       headers=headers).json()["attributes"]
    if response["current_state"] == "stopped":
        wait_time = int(config["WaitTimes"]["ServerStopped"]) * 60
    else:
        if response["resources"]["memory_bytes"] >= memory_treshold:
            if config.getboolean("RestartWarning", "Enabled"):
                req.post(request_base_url + "/command", headers=headers,
                         json={"command": config["RestartWarning"]["Command"]})
                sleep(60)
            req.post(request_base_url + "/power",
                     headers=headers, json={"signal": "restart"})
            wait_time = int(config["WaitTimes"]["ServerRestarting"]) * 60
        else:
            wait_time = int(config["WaitTimes"]["ServerRunning"]) * 60
    sleep(wait_time)
