from nornir import InitNornir
from typing import Optional, Any
from os import environ
from getpass import getpass
from pathlib import Path
from git import Repo
from nornir.core.filter import F

class newHelper():

    def __init__(self, 
                 config_file: Optional[str] = None, 
                 username: Optional[str] = None, 
                 password: Optional[str] = None, 
                 filter: Optional[F] = None, 
                 **kwargs: Any) -> None:
        
        nr = InitNornir(config_file = config_file) if config_file is not None else InitNornir(**kwargs)

        nr.inventory.defaults.username = username or environ['NORNIR_USERNAME']
        nr.inventory.defaults.password = password or environ['NORNIR_PASSWORD']
        if nr.inventory.defaults.username is None:
            nr.inventory.defaults.username = input("Username: ")
        if nr.inventory.defaults.password is None:
            nr.inventory.defaults.password = getpass("Password: ")

        if filter is not None:
            nr = nr.filter(filter)

        ## pulling from the nornir config file
        ## defaults to empty if no value found
        self.saved_configs_root = nr.config.user_defined.get("saved_configs_path") or ""
        self.template_path = nr.config.user_defined.get("template_path") or ""

        ## make sure saved configuration root folder exists
        Path(f"{self.saved_configs_root}").mkdir(exist_ok = True)

        ## original_nr allows multiple filter calls
        self.nr, self.original_nr = nr, nr

        ## check if configs are managed by git repo
        try:
            self.repo = Repo(self.saved_configs_root)
        except Exception:
            self.repo = None

