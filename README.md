# homelab-nornir
This is is the code that I've written to interact with Cisco routers in my homelab. 

Inventory for nornir is pulled from Netbox.

## quickstart

Requires python < 3.14

    py -m venv venv
    venv/scripts/activate
    py -m pip install --upgrade pip
    pip install -r requirements.txt

    py main.py --send-command "show version"