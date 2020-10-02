# -*- coding: utf-8 -*-
import os,zipfile,sys,shutil,glob,subprocess,re,threading,time,datetime,shutil
from moviepy.editor import VideoFileClip
import PIL
from PIL import Image
import math


class MakeVideo:

    def __init__(self, app, message, chat_id):
        self.app = app
        self.message_zip = message

        self.chat_id = chat_id

        self.message_reply = self.message_zip.reply_text(text="Downloading Zip to Cook...Plz Wait")
        self.message_reply_id = self.message_reply.message_id

        # Downloading of Zip is started

        self.zip_location = self.download_zip(self.message_zip)

        # Downloading of Zip is finished

        self.app.edit_message_text(chat_id=self.chat_id, text="Downloading Done...", message_id=self.message_reply_id)

        self.zip_name = os.path.basename(self.zip_location)
        self.content_name = self.zip_name[:-4]
        self.video_name = self.content_name + '.mp4'
        self.video_location = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Videos', self.video_name)
        self.pwd = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Temp', self.content_name)
        self.list_path = os.path.join(self.pwd, "list.txt")
        self.ffmpeg_command_fast = str(
            'ffmpeg -y -f concat  -i "' + str(self.list_path) + '" -safe 0  -c copy' + ' "' + str(
                self.video_location) + '" ')
        self.ffmpeg_command_slow = str(
            'ffmpeg -y -f concat  -i "' + str(self.list_path) + '" -safe 0  ' + ' "' + str(self.video_location) + '" ')
        self.thumbnail_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Videos', 'thumbnail.jpg')

        self.is_create_dir = False
        self.is_extracted = False
        self.is_moved = False
        self.is_renamed = False
        self.is_deleted = False
        self.is_created_list = False
        self.is_sorted_list = False
        self.is_cooked = False
        self.is_send = False
        self.is_msg_send = False
        self.is_failed = False

    def start(self):

        self.start_timer = self.timer('start')

        try:

            self.create_dir(self.pwd)
            self.is_create_dir = True
        except:
            self.app.edit_message_text(chat_id=self.chat_id, text="Error While Creating PWd",
                                       message_id=self.message_reply_id)
            pass

        if self.is_create_dir == True:

            try:
                self.zip_extract(self.zip_location, self.pwd)
                self.is_extracted = True
            except:
                self.clear()
                self.app.edit_message_text(chat_id=self.chat_id, text="Error While Zip Extracting",
                                           message_id=self.message_reply)
                pass
        if self.is_extracted == True:
            try:
                self.move_to_root_folder(self.pwd, self.pwd)
                self.is_moved = True
            except:
                self.clear()
                self.app.edit_message_text(chat_id=self.chat_id, text="Error While Moving Clips",
                                           message_id=self.message_reply_id)
                pass

        if self.is_moved == True:
            try:
                self.rename(self.pwd)
                self.is_renamed = True
            except:
                self.clear()
                self.app.edit_message_text(chat_id=self.chat_id, text="Error While Renaming Clips",
                                           message_id=self.message_reply_id)
                pass
        if self.is_renamed == True:
            try:
                self.delete(self.pwd)
                self.is_deleted = True
            except:
                self.clear()
                pass
        if self.is_deleted == True:
            try:
                self.create_list(self.pwd)
                self.is_created_list = True

            except:
                self.clear()
                self.app.edit_message_text(chat_id=self.chat_id, text="Error While Deleting Small clips",
                                           message_id=self.message_reply_id)
                pass
        if self.is_created_list == True:
            try:
                self.sort_nicely(self.list_path)
                self.is_sorted_list = True
            except:
                self.clear()
                self.app.edit_message_text(chat_id=self.chat_id, text="Error While Creating List",
                                           message_id=self.message_reply_id)
                pass

        if self.is_sorted_list == True:
            try:
                self.app.edit_message_text(chat_id=self.chat_id, text="Cooking Started ...",
                                           message_id=self.message_reply_id)
                self.ffmpeg_output = self.cook_videos(self.ffmpeg_command_fast)
                print(self.ffmpeg_output)
                self.ffmpeg_output = str(self.ffmpeg_output)

                self.is_failed = self.ffmpeg_output.find("Conversion failed")
            except:
                # self.clear()
                self.app.edit_message_text(chat_id=self.chat_id, text="Error While Cooking Fast",
                                           message_id=self.message_reply_id)
                pass

        if self.is_failed != -1:
            try:
                self.app.edit_message_text(chat_id=self.chat_id,
                                           text="Fast Method did not work..Cooking in slow Method ...Plz Wait ",
                                           message_id=self.message_reply_id)
                self.ffmpeg_output = self.cook_videos(self.ffmpeg_command_slow)
                self.ffmpeg_output = str(self.ffmpeg_output)
                self.is_cooked = True
            except:

                self.app.edit_message_text(chat_id=self.chat_id, text="Error While Cooking slow",
                                           message_id=self.message_reply_id)
                pass
        else:
            if os.path.isfile(self.video_location):

                self.is_cooked = True
                self.app.edit_message_text(chat_id=self.chat_id, text="Cooking Finished ...",
                                           message_id=self.message_reply_id)
            else:
                self.app.edit_message_text(chat_id=self.chat_id, text="Video not cooked...",
                                           message_id=self.message_reply_id)
        if self.is_cooked == True:
            try:
                self.video_properties(self.video_location)
                self.is_got_properties = True
            except:
                print("Unable to get video properties .... Going with default values")
                self.app.edit_message_text(chat_id=self.chat_id,
                                           text="Unable to get video properties .... Going with default values",
                                           message_id=self.message_reply_id)
                self.is_got_properties = False
        if self.is_cooked == True:

            if self.is_got_properties == True:

                try:
                    self.send_video(self.content_name, self.video_location, self.thumbnail_path, self.chat_id)
                    self.is_send = True



                except:
                    self.app.edit_message_text(chat_id=self.chat_id, text="Error While Sending Video with properties",
                                               message_id=self.message_reply_id)
                    pass
            else:
                try:
                    self.send_video_without_properites(self.content_name, self.video_location, self.thumbnail_path,
                                                       self.chat_id)
                    self.is_send = True
                except:
                    self.app.edit_message_text(chat_id=self.chat_id,
                                               text="Error While Sending Video without properties",
                                               message_id=self.message_reply_id)
                    pass

        self.stop_timer = self.timer('stop')

        if self.is_send == True:
            try:
                self.msg_to_send = self.send_msg(self.content_name, self.zip_location, self.video_location,
                                                 self.start_timer, self.stop_timer)
                self.send_video_message.reply_text(text=self.msg_to_send)
                self.is_msg_send = True
            except:
                # self.clear()
                self.app.edit_message_text(chat_id=self.chat_id, text="Error While Sending Last msg",
                                           message_id=self.message_reply_id)
                pass

        if self.is_msg_send == True:
            print(self.content_name, " video is Cooked succesfully")
            msg = "Here's Your " + self.content_name
            self.app.edit_message_text(chat_id=self.chat_id, text=msg,
                                       message_id=self.message_reply_id)
        # self.clear()

    def create_dir(self, param):

        print("at  create dir")
        if not os.path.exists(param):
            os.makedirs(param)

    def download_zip(self, message):
        zip_location=message.download(
                                      block=True,

                                      )
        zip_location = self.app.download_media(message, block=True,)
        print("Printing zip path..Now ", zip_location)
        return zip_location

    def zip_extract(self, zip_location, pwd):

        print("at zip ")

        with zipfile.ZipFile(zip_location, 'r') as zip_ref:
            zip_ref.extractall(pwd)

    def move_to_root_folder(self, root_path, cur_path):

        print("at  move to root folder")

        for filename in os.listdir(cur_path):
            if os.path.isfile(os.path.join(cur_path, filename)):
                shutil.move(os.path.join(cur_path, filename), os.path.join(root_path, filename))
            elif os.path.isdir(os.path.join(cur_path, filename)):
                self.move_to_root_folder(root_path, os.path.join(cur_path, filename))
            else:
                sys.exit("Should never reach here.")
        if cur_path != root_path:
            os.rmdir(cur_path)

    def rename(self, param):

        print("at  rename ")
        path = param

        for filename in os.listdir(path):
            my_source = os.path.join(path, filename)
            new_filename = filename[:-4] + ".mp4"
            my_dest = os.path.join(path, new_filename)

            # rename() function will
            # rename all the files

            os.rename(my_source, my_dest)

        # os.remove(me)

    def delete(self, param):
        print("at  delete")

        for root, _, files in os.walk(param):
            for f in files:
                fullpath = os.path.join(root, f)
                try:
                    if os.path.getsize(fullpath) < 100 * 1024:  # set file size in kb
                        os.remove(fullpath)
                except WindowsError:
                    print("Error at Deleting")

    def create_list(self, param):

        print("at cratelist")

        os.chdir(param)
        with open("list.txt", "a") as f:
            for file in glob.glob("*.mp4"):
                # f = open("output.txt", "a")
                # print(file,file=f)
                print("file '", file, "'", file=f, sep='')

    def sort_nicely(self, list_path):
        print("at sort nicely")

        output_file = list_path

        """ Sort the given list in the way that humans expect.
        """
        with open(output_file, "r") as txt:
            file = txt.read()

        list = file.split('\n')  # converts to list
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        list.sort(key=alphanum_key)

        with open(output_file, 'w') as f:
            for item in list:
                f.write("%s\n" % item)

    def cook_videos(self, ffmpeg_command):
        print("at fast/Slow cook")

        ffmpeg_output = subprocess.run(ffmpeg_command, shell=True, capture_output=True)

        return ffmpeg_output

    def video_properties(self, video_path):
        print("at clliip duration height width")
        clip = VideoFileClip(video_path)
        self.duration = clip.duration

    def send_video(self, content_name, video_path, thumbnail_path, chat_id):

        print("at send video ")

        print("send video start")
        print(chat_id, video_path, content_name, self.duration)

        self.start=time.time()

        self.send_video_message = self.app.send_video(chat_id=chat_id,
                                                 video=video_path,
                                                 caption=content_name,
                                                 thumb=thumbnail_path,
                                                 duration=int(self.duration),
                                                 progress=self.video_progress,

                                                 )
        print("send video end")

    def send_video_without_properites(self, content_name, video_path, thumbnail_path, chat_id):

        print("at send video ")

        print("send video start")
        print(chat_id, video_path, content_name)

        self.send_video_message = self.app.send_video(chat_id=chat_id,
                                                 video=video_path,
                                                 caption=content_name,
                                                 thumb=thumbnail_path,
                                                 progress=self.video_progress,

                                                 )
        print("send video end")

    def send_msg(self, content_name, zip_path, video_path, start_timer, stop_timer):

        print("at final msg")

        video_size = os.path.getsize(video_path)
        zip_size = os.path.getsize(zip_path)
        time_taken = stop_timer - start_timer

        msg_to_send = content_name + "\n\n\n" + "Zip Size =" + str(
            self.humanbytes(zip_size)) + "      " + "Video Size =" + str(
            self.humanbytes(video_size)) + "\n\n\nTotal time taken  to cook is " + str(
            datetime.timedelta(seconds=int(time_taken)))

        return msg_to_send

    def timer(self, state):
        if state == 'start':
            start_timer = time.time()
            return start_timer
        if state == 'stop':
            stop_timer = time.time()
            return stop_timer

    def humanbytes(self, B):
        B = float(B)
        KB = float(1024)
        MB = float(KB ** 2)  # 1,048,576
        GB = float(KB ** 3)  # 1,073,741,824
        TB = float(KB ** 4)  # 1,099,511,627,776

        if B < KB:
            return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
        elif KB <= B < MB:
            return '{0:.2f} KB'.format(B / KB)
        elif MB <= B < GB:
            return '{0:.2f} MB'.format(B / MB)
        elif GB <= B < TB:
            return '{0:.2f} GB'.format(B / GB)
        elif TB <= B:
            return '{0:.2f} TB'.format(B / TB)

    def video_progress(self, current, total):
        now = time.time()
        if now>self.start:
            diff = (now - self.start)

        percentage = (current / total)*100
        speed = current / diff

        progress = "{}" "\n\n" "{}" "\n\n" "{}" "\n " "Uploaded: {}" "\n\nPercentage : {} %       Speed : {} ".format(
            ''.join(["*" for i in range(math.floor(percentage / 5))]),
            str("❚█══uploading══█❚"),
            ''.join(["*" for i in range(math.floor(percentage / 5))]),
            self.humanbytes(current) + '  of  ' + self.humanbytes(total),
            #str(datetime.timedelta(seconds=int(estimated_total_time))),
            round(percentage, 2),
            self.humanbytes(speed))



        video_progress_message = self.app.edit_message_text(
            chat_id=self.chat_id,
            text=progress,
            message_id=self.message_reply_id,

        )

    def zip_progress(self, current, total):
        percentage = (current / total) * 100
        equals_to = int(percentage / 5)
        st = str("\r[%-20s] %d%%" % ('=' * equals_to, percentage))
        download_data = str("Downloading....Zip to local machine\n\n " + st + "  " + str(
            self.humanbytes(current) + ' / ' + self.humanbytes(total)))
        video_progress_message = self.app.edit_message_text(
            chat_id=self.chat_id,
            text=download_data,
            message_id=self.message_reply_id,

        )

    def clear(self):
        print("At clear")

        if os.path.isdir(self.pwd):
            shutil.rmtree(self.pwd, ignore_errors=True)

        if os.path.isfile(self.video_location):
            os.remove(self.video_location)

        if os.path.isfile(self.zip_location):
            os.remove(self.zip_location)

        if os.path.isfile(self.pwd):
            shutil.rmtree(self.pwd, ignore_errors=True)

        if os.path.isdir(self.video_location):
            os.rmdir(self.video_location)

        if os.path.isdir(self.zip_location):
            os.rmdir(self.zip_location)



