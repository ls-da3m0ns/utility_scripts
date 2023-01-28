#!/usr/bin/env python3
"""
organizes a folder into subfolders based on file extension

creates a background service that monitors a folder for new files
and moves them into subfolders based on their file extension
"""

import os
import time
import shutil
from typing import List, Dict, Tuple
import traceback
# folder to monitor
base_folder: str = '/home/home/Downloads/'
sub_folders: Dict[str,List[str]] = {
    "data_files" : ["csv","json","xml","txt","parquet","orc","shp","tif","shx", "kml"],
    "zips" : ["zip","tar","gz","bz2","rar"],
    "documents" : ["doc","docx","pdf","xls","xlsx","ppt","pptx", 
                    "rtf", "odt", "ods", "odp", "oxps", "epub"],
    "scripts" : ["ipynb", "py", "sh", "js"],
    "video_files" : ["mp4","mkv","avi","mov","wmv","flv","webm"],
    "audio_files" : ["mp3","wav","ogg","flac","wma"],
    "image_files" : ["jpg","jpeg","png","gif","bmp","svg"],
}

def _create_base_folders() -> None:
    """
    creates the base folders if they don't exist
    """
    for folder in sub_folders:
        if not os.path.exists(base_folder + folder):
            os.makedirs(base_folder + folder)

def _get_file_extension(file_name: str) -> str:
    """
    returns the file extension of a file
    """
    return file_name.split('.')[-1]

def _move_file(file_name: str) -> None:
    """
    moves a file into a subfolder based on its extension
    """
    file_extension: str = _get_file_extension(file_name)
    for folder in sub_folders:
        if file_extension in sub_folders[folder] and os.path.isfile(base_folder + file_name):
            shutil.move(base_folder + file_name, base_folder + folder + '/' + file_name)

def _get_file_list() -> List[str]:
    """
    returns a list of files in the base folder
    """
    
    return os.listdir(base_folder) 

if __name__ == '__main__':
    _create_base_folders()
    try:
        file_list: List[str] = _get_file_list()
        for file_name in file_list:
            _move_file(file_name)
    except Exception as e:
        print(traceback.format_exc())


