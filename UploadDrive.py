import os


def google_drive_auth():
    global drive


class Upload:


    def __init__(self,app,message,upload_to,drive,chat_id):

        self.app=app
        self.chat_id=chat_id
        self.message=message
        chandan_zips_reasoning = '1XnppfJ1G4a8RbSZF9HALUEJD38x2hSEu'
        chandan_zips_arithematics = '1cpw61nGRn_TfOHa2FtrOy9h'
        self.team_drive_id = '0AA-mJZpOW19XUk9PVA'


        if upload_to==False:
            self.folder_id=chandan_zips_reasoning
        if upload_to==True:
            self.folder_id=chandan_zips_arithematics
        self.drive=drive






    def download(self):
        self.reply=self.message.reply_text(text='Downloading Started...Plz Wait')
        self.reply_id = self.reply.message_id

        self.zip_location=self.app.download_media(self.message,block=True,)

        self.app.edit_message_text(chat_id=self.chat_id, text="Downloading Finished...Uploading to Google Drive",
                                       message_id=self.reply_id)
        self.zip_name = os.path.basename(self.zip_location)[:-4]




    def uploader(self):

        f = self.drive.CreateFile({
            'title': self.zip_name,
            'mimetype': 'zip',
            'parents': [{
                'kind': 'drive#fileLink',
                'teamDriveId': self.team_drive_id,
                'id': self.folder_id
            }]
        })
        f.SetContentFile(self.zip_location)
        print(self.zip_location)
        self.app.edit_message_text(chat_id=self.chat_id,text="Uploading to Google drive started ....",message_id=self.reply_id)
        try:
            f.Upload(param={'supportsTeamDrives': True})
        except Exception as e:
            print(e)

            self.app.edit_message_text(chat_id=self.chat_id, text="Unable to Upload ... Try Again",
                                       message_id=self.reply_id)



    def clear(self):
        self.app.edit_message_text(chat_id=self.chat_id,
                                   text="Uploaded to Google drive  .... Now U can send new Task",
                                   message_id=self.reply_id)
        try:
            if os.path.isfile(self.zip_location):
                os.remove(self.zip_location)

        except:
           pass



