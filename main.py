
if __name__ == "__main__":
    from helper import Helper
    from nornir.core.filter import F
    from nornir_utils.plugins.functions import print_result
    from logging import DEBUG
    import argparse
    import customTasks

    parser = argparse.ArgumentParser(prog = "nornir", description = "manage and/or configure CML routers using nornir")
    parser.add_argument("--config", help = "yaml config file for nornir")
    parser.add_argument("--verbose", "-v", action = "store_true", help = "Verbose output")
    
    command_group_top = parser.add_argument_group("Command options", description = "Command to execute. Only one may be selected.")
    command_group = command_group_top.add_mutually_exclusive_group()
    command_group.add_argument("--generate-template", action = "store_true", help = "Generate configuration from jinja2 templates")
    command_group.add_argument("--apply-template", action = "store_true", help = "Generate and apply configuration from jinja2 templates")
    command_group.add_argument("--send-command", help = "Command to send to devices. Command will not be executed in configure terminal.")
    command_group.add_argument("--send-config", help = "Configure command to send to devices.")
    command_group.add_argument("--save-config", action = "store_true", help = "Save configuration of devices. Equivalent to `write memory`.")
    command_group.add_argument("--backup-config", action = "store_true", help = "Backup configuration of devices running-configuration to local files. " \
                                "If the folder where the configurations are stored is a git reposiroty, any changes will be commited.")
    command_group.add_argument("--validate-config", action = "store_true", help = "Validates current running configuration using TTP.")
    
    filter_group_top = parser.add_argument_group("Filtering options", description = "group and host options are mutually exclusive.")
    filter_group_top.add_argument("--group-and", action = "store_true", dest = "group_and", help = "Use AND logic for groups.",)
    filter_group = filter_group_top.add_mutually_exclusive_group()
    filter_group.add_argument("--host", action = "append", help = "Host to filter on. Uses OR with other hosts.")
    filter_group.add_argument("--group", action = "append", help = "Group to filter on. Uses OR by default with other groups.")
    
    
    args = parser.parse_args()

    ## building the filter to be used
    ## hosts and groups are mutually exclusive. Only one or the other.
    arg_filter = None
    ## hosts
    if args.host is not None:
        for host in args.host:
            if arg_filter is None:
                arg_filter = F(name = host)
            else:
                arg_filter |= F(name = host) # or
    ## groups
    if args.group is not None:
        for group in args.group:
            if arg_filter is None:
                arg_filter = F(groups__contains = group)
            elif args.group_and:
                arg_filter &= F(groups__contains = group) # and
            else:
                arg_filter |= F(groups__contains = group) # or

    arg_config = args.config if args.config is not None else "config.yml"

    h = Helper(arg_config)
    if arg_filter is not None: h.filter(arg_filter)


    if args.generate_template:
        result = h.run(task = customTasks.template)
    elif args.apply_template:
        result = h.run(task = customTasks.template, apply = True)
    elif args.send_command:
        result = h.run(task = customTasks.command, command = args.send_command)
    elif args.send_config:
        result = h.run(task = customTasks.command, command = args.send_config, config = True)
    elif args.save_config:
        result = h.run(task = customTasks.save_configuration)
    elif args.backup_config:
        result = h.run(task = customTasks.backup_configuration, dir = getattr(h, "saved_configs_root", None))
    elif args.validate_config:
        result = h.run(task = customTasks.validate_configuration)
    
    if args.verbose: 
        print_result(result, severity_level = DEBUG)