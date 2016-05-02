__author__ = 'Vladimir'

import argparse
import os
import sys
import shutil


def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class FolderInfo:
    def __init__(self, root, rel_path, name):
        self.root = root
        self.rel_path = rel_path
        self.name = name

    def is_equals(self, to):
        if self.rel_path == to.rel_path and self.name == to.name:
            return True
        return False

    def get_full_name(self):
        return os.path.join(os.path.join(self.root, self.rel_path), self.name)

    def delete(self):
        full_name = self.get_full_name()
        try:
            os.rmdir(full_name)
        except Exception as e:
            print('Error delete folder {}: {}'.format(full_name, e))


class FileInfo(FolderInfo):
    def __init__(self, root, rel_path, name, size, change_time, crc):
        FolderInfo.__init__(self, root, rel_path, name)
        self.size = size
        self.change_time = change_time
        self.crc = crc

    def is_equals(self, to):
        if self.rel_path == to.rel_path and self.name == to.name and self.size == to.size and is_close(
                self.change_time, to.change_time) and self.crc == to.crc:
            return True
        return False

    def delete(self):
        full_name = self.get_full_name()
        try:
            os.remove(full_name)
        except Exception as e:
            print('Error delete file {}: {}'.format(full_name, e))

    def copy_to(self, folder):
        source_file = self.get_full_name()
        destination_file = os.path.join(folder, self.name)
        try:
            shutil.copy2(source_file, destination_file)
        except Exception as e:
            print('Error copy {} to {}: {}'.format(source_file, destination_file, e))


def list_dir(folder):
    result_files = {}
    result_folders = {}
    for root, folders, files in os.walk(folder):
        for current_file in files:
            relative_path = os.path.relpath(root, folder)
            if relative_path == '.':
                relative_path = ''
            stat = os.stat(os.path.join(root, current_file))
            key = os.path.join(relative_path, current_file)
            result_files[key] = FileInfo(folder, relative_path, current_file, stat.st_size, stat.st_mtime, None)
        for current_folder in folders:
            relative_path = os.path.relpath(root, folder)
            if relative_path == '.':
                relative_path = ''
            key = os.path.join(relative_path, current_folder)
            result_folders[key] = FolderInfo(folder, relative_path, current_folder)
    return result_folders, result_files


parser = argparse.ArgumentParser(description='Mirroring folder', add_help=True)
parser.add_argument('source', nargs=1, help='Source folder')
parser.add_argument('destination', nargs=1, help='Destination folder')
parser.add_argument('--test', dest='test', action='store_true', help='Only test')
parser.add_argument('--quiet', dest='quiet', action='store_true', help='Quiet mode - do not display any messages')
args = parser.parse_args()

source_dir = args.source[0]
dest_dir = args.destination[0]
is_test = args.test
is_quiet = args.quiet

if not os.path.isdir(source_dir):
    print('Directory {} not exists'.format(source_dir))
    sys.exit(0)

if os.path.exists(dest_dir) and not os.path.isdir(dest_dir):
    print('{} is nod directory'.format(dest_dir))
    sys.exit(0)

source_folder_list, source_file_list = list_dir(source_dir)
dest_folder_list, dest_file_list = list_dir(dest_dir)

# Deleting files from destination folder
for file_name, dest_object in dest_file_list.items():
    if file_name not in source_file_list or not dest_object.is_equals(source_file_list[file_name]):
        if not is_quiet:
            print('Delete file {}'.format(dest_object.get_full_name()))
        if not is_test:
            dest_object.delete()
        del dest_file_list[file_name]

# Deleting folders from destination folder
for folder_name, dest_object in dest_folder_list.items():
    if folder_name not in source_folder_list:
        if not is_quiet:
            print('Delete folder {}'.format(dest_object.get_full_name()))
        if not is_test:
            dest_object.delete()
        del dest_folder_list[folder_name]

# Create folders in destination folder
for folder_name, source_object in source_folder_list.items():
    if folder_name not in dest_folder_list:
        full_folder = os.path.join(dest_dir, folder_name)
        if not is_quiet:
            print('Create folder {}'.format(full_folder))
        if not is_test:
            try:
                os.makedirs(full_folder)
            except Exception as e:
                print('Error create directory {}: {}'.format(full_folder, e))

# Copy files
for file_name, source_object in source_file_list.items():
    if file_name not in dest_file_list:
        dest_folder = os.path.join(dest_dir, source_object.rel_path)
        if not is_quiet:
            print('Copy file {} to {}'.format(source_object.get_full_name(), dest_folder))
        if not is_test:
            source_object.copy_to(dest_folder)
