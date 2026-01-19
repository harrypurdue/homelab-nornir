from helper import helper
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
import logging

## Example Usage

## Init the helper
my_helper = helper(config_file = "config.yml")

## Show command
result = my_helper.send_command_all(command_string = "show ip route", use_textfsm = True)
print_result(result)

## Config Change
## Backup Config
my_helper.backup_configuration()
result = my_helper.send_config_all(config_commands = "logging host 1.1.1.1")
print_result(result)

## Save Config
result = my_helper.save_configuration()
print_result(result)

## Config Change 2
result = my_helper.send_config_all(config_commands = "no logging host 1.1.1.1")
save = my_helper.save_configuration()
print_result(result)
print_result(save)

## Filter Inventory
my_helper.filter(F(name = "r1"))

## Generate and apply Template
result = my_helper.template(apply = True)
print_result(result, severity_level = logging.DEBUG) # Template generation and application require DEBUG level for result viewing.

## Filter Again
my_helper.filter(F(name = "r4"))

## Generate template
result = my_helper.template()
print_result(result, severity_level = logging.DEBUG) # Template generation and application require DEBUG level for result viewing.


## Automatic rollback using Cisco IOS Archive
## Auto rollback in 10 minutes if configuration is not confirmed
## TODO: Reverting changes for individual hosts instead of for all hosts if one of the hosts fails.
result = my_helper.send_config_all(config_commands = "logging host 1.2.3.4", config_mode_command = "config terminal revert timer 10")
if not result.failed:
    ## config result is not failed
    my_helper.send_command_all(command_string = "configure confirm")
