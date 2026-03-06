from helper import Helper
import customTasks

h = Helper("config.yml")
res = h.run(task = customTasks.command, command = "show version", use_textfsm = True)

for host in res:
    print(res[host][0].result)
    breakpoint()
