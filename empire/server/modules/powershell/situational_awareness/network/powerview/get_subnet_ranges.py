from __future__ import print_function

import pathlib
from builtins import object, str
from typing import Dict

from empire.server.common.empire import MainMenu
from empire.server.core.module_models import EmpireModule
from empire.server.utils.module_util import handle_error_message


class Module(object):
    @staticmethod
    def generate(
        main_menu: MainMenu,
        module: EmpireModule,
        params: Dict,
        obfuscate: bool = False,
        obfuscation_command: str = "",
    ):
        list_computers = params["IPs"]

        # read in the common powerview.ps1 module source code
        module_source = (
            main_menu.installPath
            + "/data/module_source/situational_awareness/network/powerview.ps1"
        )
        if obfuscate:
            obfuscated_module_source = module_source.replace(
                "module_source", "obfuscated_module_source"
            )
            if pathlib.Path(obfuscated_module_source).is_file():
                module_source = obfuscated_module_source

        try:
            with open(module_source, "r") as f:
                module_code = f.read()
        except Exception:
            return handle_error_message(
                "[!] Could not read module source path at: " + str(module_source)
            )

        if obfuscate and not pathlib.Path(obfuscated_module_source).is_file():
            script = main_menu.obfuscationv2.obfuscate(module_code, obfuscation_command)
        else:
            script = module_code

        script_end = (
            "\n"
            + """$Servers = Get-DomainComputer | ForEach-Object {try{Resolve-DNSName $_.dnshostname -Type A -errorAction SilentlyContinue}catch{Write-Warning 'Computer Offline or Not Responding'} } | Select-Object -ExpandProperty IPAddress -ErrorAction SilentlyContinue; $count = 0; $subarry =@(); foreach($i in $Servers){$IPByte = $i.Split("."); $subarry += $IPByte[0..2] -join"."} $final = $subarry | group; Write-Output{The following subnetworks were discovered:}; $final | ForEach-Object {Write-Output "$($_.Name).0/24 - $($_.Count) Hosts"}; """
        )

        if list_computers.lower() == "true":
            script_end += "$Servers;"

        for option, values in params.items():
            if option.lower() != "agent" and option.lower() != "outputfunction":
                if values and values != "":
                    if values.lower() == "true":
                        # if we're just adding a switch
                        script_end += " -" + str(option)
                    else:
                        script_end += " -" + str(option) + " " + str(values)

        outputf = params.get("OutputFunction", "Out-String")
        script_end += (
            f" | {outputf} | "
            + '%{$_ + "`n"};"`n'
            + str(module.name.split("/")[-1])
            + ' completed!"'
        )

        if obfuscate:
            script_end = main_menu.obfuscationv2.obfuscate(
                script_end, obfuscation_command
            )
        script += script_end
        script = main_menu.obfuscationv2.obfuscate_keywords(script)

        return script
