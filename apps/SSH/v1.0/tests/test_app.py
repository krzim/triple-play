from apps.SSH.v1_0.src.app import SSH

import pytest 
import os, sys

ip = '127.0.0.1'
port = 22
username = 'osboxes'
password = 'osboxes.org'

def test_execute():
	app = SSH()
	args = ['echo test2', 'echo test3', 'cd']
	answer = app.exec_command(args, ip, port, username, password)
	assert answer[1] == 'Success'

def test_sftp_put():
	app = SSH()
	answer = app.sftp_put("/home/osboxes/Desktop/triple-play/apps/SSH/v1_0/tests/local.txt", 
		"/home/osboxes/Desktop/triple-play/apps/SSH/v1_0/tests/remote.txt",
		ip, port, username, password)
	assert answer[1] == 'Success'
	fd = os.open("apps/SSH/v1_0/tests/local.txt",os.O_RDWR)
	ret = os.read(fd,12)
	fd2 = os.open("apps/SSH/v1_0/tests/remote.txt",os.O_RDWR)
	ret2 = os.read(fd2,12)
	assert ret == ret2
	assert ret == b'local'
	os.close(fd)
	os.close(fd2)

def test_sftp_get():
	app = SSH()
	answer = app.sftp_get("/home/osboxes/Desktop/triple-play/apps/SSH/v1_0/tests/local2.txt", 
		"/home/osboxes/Desktop/triple-play/apps/SSH/v1_0/tests/remote2.txt",
		ip, port, username, password)
	assert answer[1] == 'Success'
	fd = os.open("apps/SSH/v1_0/tests/local2.txt",os.O_RDWR)
	ret = os.read(fd,12)
	fd2 = os.open("apps/SSH/v1_0/tests/remote2.txt",os.O_RDWR)
	ret2 = os.read(fd2,12)
	assert ret == ret2
	assert ret == b'remote'
	os.close(fd)
	os.close(fd2)

def test_run_shell():
	app = SSH()
	answer = app.run_shell_script_remotely("/home/osboxes/Desktop/triple-play/apps/SSH/v1_0/tests/shell_script.txt",
		ip, port, username, password)
	assert answer[1] == 'Success'
	
def test_shutdown():
	app = SSH()
	answer = app.shutdown(ip, port, 'osboxes', password)
	assert answer[0] == True
	assert answer[1] == 'Success'