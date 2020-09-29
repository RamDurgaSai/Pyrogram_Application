import time

from pyrogram import Client,filters
import os,zipfile,sys,shutil,glob,subprocess,re,threading,time,datetime,shutil
from moviepy.editor import VideoFileClip
import PIL
from PIL import Image

from UploadDrive import Upload

from MakeVideo import MakeVideo
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import logging



logging.basicConfig(filename="log.txt",
                    filemode='a',level=logging.INFO,
                    format='%(asctime)s - %(message)s')



logging.info("Program Execution Started....")


zipvy=-455442438






logging.info("Google Drive Authentication ... Done")



api_id = 1681659
api_hash = "52206d87f2f7574e070ed39a17af6b2d"
app = Client("my_account", api_id=api_id, api_hash=api_hash)



upload_to=None
cook=None

def auth():
    global drive
    gauth = GoogleAuth()

    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")

    if gauth.credentials is None:
        # Authenticate if they're not there

        # This is what solved the issues:
        gauth.GetFlow()
        gauth.flow.params.update({'access_type': 'offline'})
        gauth.flow.params.update({'approval_prompt': 'force'})

        gauth.LocalWebserverAuth()

        #message.reply_text(text="Google Drive authentication needed ... Contact @RamDurgaSai")

    elif gauth.access_token_expired:

        # Refresh them if expired
        #message.reply_text(text="Google Drive authentication token is expired ... Contact @RamDurgaSai")
        gauth.Refresh()
    else:

        # Initialize the saved creds

        gauth.Authorize()

    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")

    drive = GoogleDrive(gauth)




@app.on_message(filters.chat(zipvy)&filters.command(commands='send-log',prefixes='#'))
def my_handler_log(client,message):
    app.send_document(chat_id='zipvy',
                      document='log.txt',
                      caption="Here's Your Log",
                      )


@app.on_message(filters.chat(zipvy)&filters.command(commands='cook',prefixes='#', ))
def my_handler_stop(client,message):
    global  cook
    cook=True #True for Cooking
    message.reply_text(text="Now UpComing Zips will be Cooked")


@app.on_message(filters.chat(zipvy) & filters.command(commands='upload',prefixes='#', ))
def my_handler_stop(client,message):
    global  cook
    cook=False
    #True for Cooking
    message.reply_text(text="Now UpComing Zips will be Uploaded to Google Drive")

@app.on_message(filters.chat(zipvy)&filters.command(commands='upload-to-r',prefixes='#', ))
def my_handler_stop(client,message):
    global upload_to
    print("at upload to r")
    upload_to= False #False for Reasoning Folder
    message.reply_text(text="Now zips sends to Reasoning folder")

@app.on_message(filters.chat(zipvy)&filters.command(commands='upload-to-a',prefixes='#',))
def my_handler_stop(client,message):
    global upload_to
    print("at upload to a")
    upload_to = True #True for Airthematic Folder
    message.reply_text(text="Now zips sends to Arithmatic folder")



@app.on_message(filters.chat(zipvy)&filters.command(commands='clear',prefixes='#',case_sensitive=False))
def my_handler_stop(client,message):
    message.reply_text(text="clearing temp Directories...")
    # MakeVideo.clear_base()


@app.on_message(filters.chat(zipvy) & filters.document)
def my_handler(client, message):
    global zipvy
    global cook
    global upload_to
    if cook==None:
        message.reply_text(text="Cooking/Uploading not defined...Try\n"
                                " #cook (for cooking videos) \n "
                                "#upload(for uploading to Google Drive")

    if cook==True:
        #print(message)
        my_objects = {}
        message_id = message.message_id
        name = 'obj_{}'.format(message_id)
        my_objects[name] = my_objects.get(name, MakeVideo(app,message,zipvy))
        my_objects[name].start()
        my_objects[name].clear()

    if cook==False:
        if upload_to==None:

            message.reply_text(text="Airthmatic/Reasoning not defined...Try\n"
                                    " #upload-to-r (for uploading to Rasoning Folder) \n "
                                    "#upload-to-a(for uploading to Airthmatic Folder")

        elif upload_to==True or upload_to==False:
            print("going to uploader")
            auth()
            uploader = Upload(app, message, upload_to, drive,chat_id='upload_to_drive')
            print("going to downlaod")
            uploader.download()
            print("Going to upload")
            uploader.uploader()
            print("Going to upload")
            uploader.clear()
            print("end of printer")







app.run()