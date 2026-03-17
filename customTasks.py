from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config, netmiko_save_config
from nornir_jinja2.plugins.tasks import template_file
from nornir.core.task import Result, Task
from nornir.core.exceptions import NornirExecutionError
from deepdiff import DeepDiff
from typing import Any

def command(task: Task, command: str | list, config: bool = False, **kwargs: Any) -> Result:
    if config:
        task_ = netmiko_send_config
        command_key = "config_commands"
    elif isinstance(command, str):
        task_ = netmiko_send_command
        command_key = "command_string"
    else:
        raise Exception(f"Error: `command` expected to be string when config is False")

    run_params = {"task" : task_, command_key : command}

    result = task.run(**run_params, **kwargs)

    return Result(host = task.host,
                result = result[0].result,
                failed = result.failed,
                changed = result.changed)


def template(task: Task, template: str = "base.j2", templates_path: str = "templates/", apply: bool = False) -> Result:
    """
    Generates or applys jinja2 templates to devices.
    
    :param task: Nornir task object
    :param apply: Apply the generated template to the device
    :return: Returns a Nornir Result object with the results of the generation and/or application of the template
    """
    # load data for template
    template_vars = task.host.extended_data()

    # name conflicts with Task/Result object return value
    del template_vars["name"]

    templates_path += task.host.platform

    changed = False

    # generate template
    generated_template = task.run(task = template_file, template = template, path = templates_path, **template_vars)
    failed = generated_template.failed
    result = generated_template[0].result

    if apply:
        applied_result = task.run(task = netmiko_send_config, config_commands = generated_template[0].result.splitlines())
        failed = applied_result.failed
        changed = applied_result.changed
        result = applied_result[0].result

    return Result(host = task.host, 
                #   result = f"host: {task.host} changed: {changed} failed: {failed}",
                    result = result,
                    changed = changed, 
                    failed = failed)


def validate_configuration(task: Task) -> Result:
    """
    Compares the intended configuration to the actual configuration on the device and displays the differences.

    The intended configuration is pulled from the self.nr object which is pulled from the netbox config context.

    ttp templates used for comparison are stored under ./templates/ttp

    :return: Returns a Result object where the result is an iterable of dictionaries. The key of the dictionary is the host and the value is a list of 
    dictionaries where the key is the configuration item and the value is the change between the current configuration
    and the intended configuration.
    
    """
    result = task.run(task = command, command = "show run", use_ttp = True, ttp_template = "./templates/ttp/")
    return_list = []
    for host in result:
        tmp = {host : []}
        for configuration_item in task.host.data["config_context"]:
            if configuration_item in result[0].result[0][0]:
                current_config = result[0].result[0][0][configuration_item]
                intended_config = task.host.data["config_context"][configuration_item]
                diff = DeepDiff(intended_config, current_config)
                tmp[host].append({configuration_item : diff})
        return_list.append(tmp)

    return Result(host = task.host,
                    changed = False,
                    failed = False,
                    result = return_list)

def save_configuration(task: Task) -> Result:
    result = task.run(task = netmiko_save_config)

    return Result(host = task.host,
                    result = result[0].result,
                    changed = result.changed,
                    failed = result.failed)

def backup_configuration(task: Task, dir: str | None = None) -> Result:
    if dir is None:
        return Result(host = task.host,
                      result = "Failed to backup configuration. `dir` is not set.",
                      changed = False,
                      failed = True)

    result = task.run(task = command, command = "show run")

    running_config = result[0].result

    with open(f"{dir}/{task.host}.txt", "w") as f:
        f.write(running_config)

    return Result(host = task.host,
                    result = running_config,
                    changed = result.changed,
                    failed = result.failed)

        
    
    