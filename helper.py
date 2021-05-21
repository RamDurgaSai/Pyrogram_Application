import os
import re
import shutil , sys
from zipfile import ZipFile
from os.path import splitext
from py7zr import SevenZipFile

def unzip(zip_location,clips_path,update_progress):
    #If file is a .zip file
    if splitext(zip_location)[1] == ".zip":
        zip_file = ZipFile(zip_location)

        uncompress_size = sum((file.file_size for file in zip_file.infolist()))

        extracted_size = 0

        for file in zip_file.infolist():
            extracted_size += file.file_size
            update_progress(extracted_size * 100 / uncompress_size)
            zip_file.extract(member = file,
                            path = clips_path)
    if splitext(zip_location)[1] ==".7z":
        zip_file = SevenZipFile(zip_location)
        zip_file.extractall(path = zip_location,
                            callback =update_progress)
        zip_file.close()


def move_to_root_folder(root_path, cur_path):
    for filename in os.listdir(cur_path):
        if os.path.isfile(os.path.join(cur_path, filename)):
            shutil.move(os.path.join(cur_path, filename), os.path.join(root_path, filename))
        elif os.path.isdir(os.path.join(cur_path, filename)):
            move_to_root_folder(root_path, os.path.join(cur_path, filename))
        else:
            sys.exit("Should never reach here.")
    if cur_path != root_path:
        os.rmdir(cur_path)

def sort_list(list):

    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    list.sort(key=alphanum_key)

    return list
def delete_small_clips(param):
        deleted_clips = []
        for root, _, files in os.walk(param):
            for f in files:
                fullpath = os.path.join(root, f)
                try:
                    if os.path.getsize(fullpath) < 100 * 1024:  # set file size in kb
                        deleted_clips.append(f)
                        os.remove(fullpath)
                except:
                    pass
        return sort_list(deleted_clips)


def delete_all_clips(param):
    for root, _, files in os.walk(param):
        for f in files:
            fullpath = os.path.join(root, f)
            try:

                os.remove(fullpath)
            except:
                pass



def merge(clips_path,video_location,call_back):
    clips_list = []
    for filename in os.listdir(clips_path):
        clips_list.append(filename)
    files = sort_list(clips_list)
    video = open(video_location, 'wb')
    count = 1
    for file in files:
        clip = open(os.path.join(clips_path, file), "rb")
        shutil.copyfileobj(clip, video)
        clip.close()

        call_back(count,file,len(files))
        count += 1

    video.close()


