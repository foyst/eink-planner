# Eink-Planner

## How to provision the Pi
`ansible-playbook -i "raspberrypi.local," -e "debug_mode=0 todoist_api_token=<your token here> ansible/playbook.yml`

Or if you prefer, use an inventory.ini file with your target like so:
```
[targets]

raspberrypi.local debug_mode=0 todoist_api_token=<your token here>
```
And run 

``ansible-playbook -i ansible/inventory.ini ansible/playbook.yml``

If you're using password-based SSH you can add `--ask-pass --ask-become-pass` to the above to prompt for your password

## How to (re)generate Google Token
Run script on a device with access to a browser (could be the Pi itself if hooked up to a display or has VNC configured)

Open Google auth link printed to console output and sign in. This will generate a token.json file. Copy this across to the Pi and then restart the epaper-dashboard service with
`sudo systemctl restart eink-planner`

## Debugging tips
### Debugging the Playbook
If you're making changes to the Python code and want to quickly sync changes and rerun the service, you can use the following:

`ansible-playbook -vvv --start-at-task="Copy Python code to Pi" -i "raspberrypi.local," ansible/playbook.yml -e "debug_mode=0 todoist_api_token=<your token here>`