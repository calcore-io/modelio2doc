'''
Created on Mar 8, 2022

@author: carlo
'''

import pathlib as pl
import os


def string_to_path(path_string):
    ''' Returns a "path" object for the given string. '''
    # pathlib requires regular diagonal, not reverse diagonal
    path_string = path_string.replace("\\", "/")
    
    return pl.Path(path_string)
    
    
def folder_exists(path):
    ''' Returns "True" if the given path is an existing folder. '''
    return_value = False
    
    if type(path) is str:
        path = string_to_path(path)
     
    if path is not None and path.exists() and path.is_dir():
        return_value = True
    
    return return_value


def file_exists(path):
    ''' Returns "True" if the given path is an existing file. '''
    return_value = False
    
    if type(path) is str:
        path = string_to_path(path)
     
    if path.exists() and path.is_file():
        return_value = True
    
    return return_value

def create_folder(folder):
    """ Creates the specified folder.
    """
    if folder_exists(folder) is False:
        try:
            folder.mkdir()
        except Exception as e:
            print('Failed to create folder %s. Reason: %s' % (folder, e))
    else:
        print("Folder to be created '%s' already exists." % folder)

def delete_folder_contents(folder):
    """ Deletes contents of the given folder.
    """
    if folder_exists(folder) is True:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    delete_folder_contents(file_path)
                    shutil.rmtree(file_path)
                    log_debug('Deleted element %s' % file_path)
            except Exception as e:
                print('Failed to delete folder %s. Reason: %s' % (file_path, e))
                
def delete_file(file_name):
    """ deletes the specified file.
    """
    try:
        os.unlink(file_name)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_name, e))