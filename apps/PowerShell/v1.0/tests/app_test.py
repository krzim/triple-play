import apps.PowerShell.v1_0.src.app
from apps.PowerShell.v1_0.src.app import PowerShell

import pytest 

def test_exec_local_command():
	app = PowerShell();
	answer = app.exec_local_command("PowerShell Core (Cross-Platform)", "-Command", ["Get-Random"])
	assert answer[1] == 'Success'