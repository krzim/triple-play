import os
import stat
from datetime import datetime
import json
#from walkoff.helpers import format_exception_message
from array import array
import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class FileUtilities(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def exists_in_directory(self, path):
        if os.path.exists(path):
            return True, 'Exists'
        else:
            return False, 'NotExists'


    def create(self, filename, contents=None, overwrite=False):
        if (not overwrite) and os.path.exists(filename):
            return False, 'AlreadyExists'
        else:
            try:
                with open(filename, 'w') as new_file:
                    new_file.write(contents)
                return True, 'FileCreated'
            except IOError:
                print("Error writing or creating file.")
                return False, 'Error'


    def append(self, filename, contents, newline=False):
        try:
            with open(filename, 'a') as f:
                if newline:
                    f.write("\n")
                f.write(contents)
            return True, 'FileWritten'
        except IOError:
            print("Error writing file.")
            return False, 'Error'
            
                    
    def remove(self, filename):
        try:
            os.remove(filename)
            return True, 'Success'
        except IOError:
            print("Error deleting file")
            return False, 'Error'


    def make_read_only(self, filename):
        try:
            READ_ONLY = ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH
            cur_perms = stat.S_IMODE(os.lstat(filename).st_mode)
            os.chmod(filename, cur_perms & READ_ONLY)
            return True, 'Success'
        except IOError:
            print("Error making file read only")
            return False, 'Error'


    def make_writable(self, filename):
        try:
            WRITE_ALLOWED = stat.S_IWUSR | stat.S_IWGRP
            cur_perms = stat.S_IMODE(os.lstat(filename).st_mode)
            os.chmod(filename, cur_perms | WRITE_ALLOWED)
            return True, 'Success'
        except IOError:
            print("Error making file writable")
            return False, 'Error'


    def join_path_elements(self, elements):
        print(elements)
        return os.path.join(*elements)

    def copy_and_bitswap(self, path_from, path_to=None):
        if not os.path.exists(path_from) or not os.path.isfile(path_from):
            return 'File not found', 'FileNotFound'

        with open(path_from, 'rb') as file_in:
            exe_bytes = array('B', file_in.read())

        exe_bytes.byteswap()

        if not path_to:
            path = os.path.join('.', 'apps', 'FileUtilities', 'data')
            filename = '{}-quarantine.bin'.format(os.path.basename(path_from).split('.')[0])
            if not os.path.exists(path):
                os.mkdir(path)
            filename = os.path.join(path, filename)
        else:
            dirname = os.path.dirname(path_to)
            if dirname and not os.path.exists(dirname):
                os.mkdir(dirname)
            filename = path_to

        with open(filename, 'wb') as file_out:
            exe_bytes.tofile(file_out)

        return filename


    def read_json(self, filename):
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return 'File does not exist', 'FileDoesNotExist'
        try:
            with open(filename, 'r') as file_in:
                return json.loads(file_in.read())
        except (IOError, IOError) as e:
            return {'error': 'Could not read file', 'reason': format_exception_message(e)}, 'FileDoesNotExist'
        except ValueError:
            return 'Could not read file as json. Invalid JSON', 'InvalidJson'


    def write_json(self, data, filename):
        dirname = os.path.dirname(filename)
        if dirname and not os.path.exists(dirname):
            os.mkdir(dirname)
        with open(filename, 'w') as config_file:
            config_file.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        return 'Success'


    def stats(self, filename):
        def add_if_exists(stat, attr, name, results):
            if hasattr(stat, attr):
                results[name] = getattr(stat, attr)

        def add_time_if_exists(stat, attr, name, results):
            if hasattr(stat, attr):
                results[name] = str(datetime.fromtimestamp(getattr(stat, attr)))

        if os.path.exists(filename):
            stats = os.stat(filename)
            result = {}
            add_if_exists(stats, 'st_mode', 'mode', result)
            add_if_exists(stats, 'st_ino', 'inode', result)
            add_if_exists(stats, 'st_dev', 'device', result)
            add_if_exists(stats, 'st_nlink', 'num_links', result)
            add_if_exists(stats, 'st_uid', 'uid', result)
            add_if_exists(stats, 'st_gid', 'gid', result)
            add_if_exists(stats, 'st_size', 'size', result)
            add_if_exists(stats, 'st_blocks', 'blocks', result)
            add_if_exists(stats, 'st_blksize', 'block_size', result)
            add_if_exists(stats, 'st_rdev', 'device_type', result)
            add_if_exists(stats, 'st_flags', 'flags', result)
            add_time_if_exists(stats, 'st_atime', 'access_time', result)
            add_time_if_exists(stats, 'st_mtime', 'modification_time', result)
            add_time_if_exists(stats, 'st_ctime', 'metadata_time', result)

            return result
        else:
            return 'File does not exist', 'FileDoesNotExist'





