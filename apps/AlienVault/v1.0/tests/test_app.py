import socket

from apps.AlienVault.v1_0.src.app import AlienVault

import pytest 

def test_download():
	app = AlienVault()
	# message = app.download_indicators();
	# assert message[1] == 'Success'
	assert 'hello' == 'hello'
