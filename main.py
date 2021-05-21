from pyrogram import Client,filters
from os.path import splitext, join, exists, basename,isfile,getsize as filesize
from os import remove,mkdir, getcwd,makedirs
from py7zr import Bad7zFile
from helper import unzip, move_to_root_folder, delete_small_clips, merge, delete_all_clips
from zipfile import BadZipfile

class Application:
    GROUP_ID = "ftsihsydi"
    CURRENT_SESSION = "Pyrogram_Application"
    API_ID = 1681659
    API_HASH = "52206d87f2f7574e070ed39a17af6b2d"

    def __init__(self):
        self.message = None
        self.replied_message = None
        self.reply_text = None
        self.app = Client(session_name = self.CURRENT_SESSION,
                     api_id = self.API_ID, api_hash = self.API_HASH)
        app = self.app
        @app.on_message(filters.chat(self.GROUP_ID) & filters.document)
        def on_zip(client, message):
            self._on_zip(client, message)

    def _on_zip(self,client, message):
        self.message = message
        self.replied_message = self.message.reply_text("Please Wait")

        if message.media == True:
            self.zip_location = self.app.download_media(message = self.message,
                                                        progress = self._download_progress)
        else:
            return
        if self.is_valid_zip(self.zip_location):
            pass
        else:
            self.send_reply("Only zips are accepted")
            remove(self.zip_location)
            return


        self.zip_name = splitext(basename(self.zip_location))[0]

        self.clips_path = join(getcwd(), self.zip_name)
        self.video_folder = join(getcwd(), "videos")
        self.video_location = join(self.video_folder, self.zip_name + ".mp4")

        if not exists(self.clips_path): makedirs(self.clips_path)
        if not exists(self.video_folder):  makedirs(self.video_folder)

        try:  unzip(self.zip_location, self.clips_path,self._update_zip_extraction)

        except  (BadZipfile,Bad7zFile) :
            self.send_reply("BadZipFile/Bad7zfile or zip/7z is broken")
            return

        # move clips to root
        move_to_root_folder(self.clips_path, self.clips_path)
        delete_small_clips(self.clips_path)
        # Delete Small clips ...




        #################################################
        #                    Merging                    #
        #################################################

        try: merge(self.clips_path, self.video_location, self._update_merge_progress)
        except Exception as e:
            self.send_reply("Something went wrong at merging "+ e.__str__())

        #################################################
        #                 Uploading Vidoe               #
        #################################################

        try:
            self.app.send_video(chat_id= self.GROUP_ID,video=self.video_location,
                                caption= basename(self.video_location),
                                progress= self._upload_progress)
        except Exception as e :
            self.send_reply(" Something went wrong at merging " + e.__str__())


        try:
            delete_all_clips(self.clips_path)
            if isfile(self.zip_location):
                remove(self.zip_location)
        except Exception as e:
            self.send_reply("Something went wrong \n" + e.__str__())
            return
        self.send_reply("Here's Your " +self.zip_name)

    def _update_merge_progress(self, file_no, file_name, files):
        percentage = int(file_no * 100 / files)

        self.send_reply("Merging clips " + str(file_no) + "/" + str(files) + " " + str(int(percentage)) + "%")


    def _update_zip_extraction(self,progress):
        self.send_reply("Downloading Zip ---> " + str(progress))

    def _download_progress(self,current, total):
        self.send_reply("Downloading Zip ---> " + str(int(current * 100 //total)))
    def _upload_progress(self,current,total):
        self.send_reply("Uploading Video ---> " + str(int(current * 100 //total)))

    def run(self):
        self.app.run()

    def send_reply(self,reply_text):

        if(self.reply_text != reply_text):
            self.app.edit_message_text(chat_id=self.GROUP_ID,
                                       text=reply_text,
                                       message_id=self.replied_message.message_id)
            self.reply_text = reply_text


    def is_valid_zip(self,zip_location):
        print(isfile(zip_location))
        print(splitext(zip_location)[1])
        print(filesize(zip_location))
        if isfile(zip_location):
            if splitext(basename(zip_location))[1] != ".zip" or splitext(basename(zip_location))[1] != ".7z":
                if int(filesize(zip_location)) > 0:
                    return True
        return False

    def delete_zip(self):
        try:
            if isfile(self.zip_location):
                remove(self.zip_location)
        except OSError:
            raise OSError("Unable to delete zip")

if __name__ == '__main__':
    Application().run()