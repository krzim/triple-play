from apps.FileUtilities.v1_0.src.app import FileUtilities

import pytest 
import os

def test_exists_in_directory_true():
	app = FileUtilities()
	message = app.exists_in_directory("apps/HelloWorld/v1_0/src/app.py")
	assert message[0] == True

def test_exists_in_directory_false():
	app = FileUtilities()
	message = app.exists_in_directory("not valid")
	assert message[0] == False


def test_create_new_and_delete():
	app = FileUtilities()
	path = "apps/FileUtilities/v1_0/tests/test_create1.txt"
	# test that file does not exist yet
	assert os.path.exists(path) == False
	# test creation of new file
	message = app.create(path, "Hello, this is a test")
	assert message == (True, 'FileCreated')
	# checking content successfully changed
	assert os.path.exists(path) == True
	# delete after
	message = app.remove(path)
	assert message == (True, 'Success')
	assert os.path.exists(path) == False


def test_create_exists():
	app = FileUtilities()
	# file that already exists without overwrite
	message = app.create("apps/FileUtilities/v1_0/tests/test_create2.txt", "Hello, this is a test")
	# file that already exists with overwrite
	assert message == (False, 'AlreadyExists')
	message = app.create("apps/FileUtilities/v1_0/tests/test_create2.txt", "Hello, this is a test", True)
	# checking content successfully changed

def test_append():
	app = FileUtilities()
	path = "apps/FileUtilities/v1_0/tests/test_create2.txt"
	message = app.append(path, 'test', True)
	assert message == (True, 'FileWritten')

def test_readonly_write():
	path = "apps/FileUtilities/v1_0/tests/test_create2.txt"
	app = FileUtilities()
	# make read only
	message = app.make_read_only(path)	
	assert message == (True, 'Success') 
	# try to modify read-only
	message = app.append(path, 'test', True)
	assert message == (False, 'Error') 
	# make writable
	message = app.make_writable(path)
	assert message == (True, 'Success')
	# try to modifiy writable 
	message = app.append(path, 'test', True)
	assert message == (True, 'FileWritten') 

def test_read_json():
	path = "apps/FileUtilities/v1_0/tests/test_create3.txt"
	app = FileUtilities()
	# file does not exist
	message = app.read_json(path)
	assert message == ('File does not exist', 'FileDoesNotExist')
	# valid file path but not json
	path = "apps/FileUtilities/v1_0/tests/test_create2.txt"
	message = app.read_json(path)
	assert message == ('Could not read file as json. Invalid JSON', 'InvalidJson')
	# valid file path and json
	path = "apps/FileUtilities/v1_0/tests/test_json.txt"
	message = app.read_json(path)

def test_copy_and_bitswap():
	path_from = "apps/FileUtilities/v1_0/tests/test_create2.txt"
	#shouldn't exist yet
	path_to = "apps/FileUtilities/v1_0/tests/test_bitswap.txt"
	app = FileUtilities()
	assert os.path.exists(path_to) == False
	message = app.copy_and_bitswap(path_from, path_to)
	# path should exist now
	assert os.path.exists(path_to) == True
	#testing contents
	fd = os.open("apps/FileUtilities/v1_0/tests/test_bitswap.txt",os.O_RDWR)
	ret = os.read(fd,12)
	fd2 = os.open("apps/FileUtilities/v1_0/tests/test_create2.txt",os.O_RDWR)
	ret2 = os.read(fd2,12)
	assert ret == ret2
	#remove path
	#app.remove(path_to)



