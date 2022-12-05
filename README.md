# epaper-dashboard

## How to provision the Pi
`ansible-playbook --ask-pass --ask-become-pass -i "raspberrypi.local," ansible/playbook.yml`

## How to (re)generate Google Token
Run script on a device with access to a browser (could be the Pi itself if hooked up to a display or has VNC configured)

Open Google auth link printed to console output and sign in. This will generate a token.json file. Copy this across to the Pi and then restart the epaper-dashboard service with
`sudo systemctl restart eink-planner`

## Debugging tips
### Debugging the Playbook
If you're making changes to the Python code and want to quickly sync changes and rerun the service, you can use the following:

`ansible-playbook -vvv --ask-pass --ask-become-pass --start-at-task="Copy Python code to Pi" -i "raspberrypi.local," ansible/playbook.yml`