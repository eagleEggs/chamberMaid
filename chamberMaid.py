######################################################################################################  chamberMaid v0.1
########################################################################################################################

# IMPORTS
import PySimpleGUI
import openai
import dill
import os
import uuid
import requests
import PySimpleGUI as sg
import tkinter as tk
import warnings
from PIL import Image
from io import BytesIO
import base64

import chamberPortraits  # GUI images

sg.theme("DarkGrey11")

authorReferenceList = ["No One Specific", "Oscar Wilde", "Anne Rice", "Nathaniel Hawthorne", "Stephen King", "Voltaire", "C.S. Lewis",
                      "Shakespeare", "Mary Shelley", "Tolstoy", "Plato", "Tolkien", "J.K. Rowling", "Frank Herbert",
                       "Robert Louis Stevenson", "Dan Simmons", "Ayn Rand", "Marcus Aurelius", "R.L. Stine",
                       "Roald Dahl"]

class Chamber(object):
    '''This Object is for Building the Book Framework'''
    def __init__(self, title, sessionTitle, authorReference, moods = [],
                    iterations = 0, rewrites = 0, useWords = [],
                    locations = [], feelings = [], pageLineCount = 33, currentChapter = None,
                    spellingErrors = False, spacesErrors = False, grammarMix = False,
                    authorAge = None,
                    referenceText = None, authorReference2 = None):
        self.title = title
        self.authRef = authorReference
        self.authRef2 = authorReference2
        self.moods = moods
        self.refText = referenceText
        self.iterations = iterations
        self.rewrites = rewrites
        self.useWords = useWords
        self.spellingErrors = spellingErrors
        self.grammarMix = grammarMix
        self.locations = locations
        self.feeling = feelings
        self.pageLineCount = pageLineCount
        self.currentChapter = currentChapter
        self.sessionTitle = sessionTitle
        self.spacesErrors = spacesErrors
        self.authorAge = authorAge

    def newChapter(self):
        '''Generate a New Chapter Object'''
        pass

    def pages(self):
        '''Generate a New Page Object'''
        pass

    def book(self, page):
        pass

    def saveFile(self, newFile = False):
        '''Save to File; newFile will create a new file instead of overwriting the current'''
        pass

    def saveSession(self, new = True):
        if not new:
            dill.dump_module('/{}.pkl'.format(self.sessionTitle))
        else:
            dill.dump_module('/{}_{}.pkl'.format(self.sessionTitle, uuid.uuid4()))

    def loadSession(self):
        dill.load_module('/{}.pkl'.format(self.sessionTitle))

class Maid(object):
    """This is the API Object"""
    def __init__(self, APIKey, org):
        self.APIKey = APIKey
        self.org = org
        self.connected = False

    def connect(self):
        openai.organization = "{}".format(self.org)
        openai.api_key = "{}".format(self.APIKey)
        self.connected = True

    def listModels(self):
        modelList = openai.Model.list()
        return modelList

    def curlSheets(self):
        if self.connected:
            print("Cleaning Chamber...")
            curledSheets = openai.Completion.create(
                engine='text-davinci-003',  # Determines the quality, speed, and cost.
                temperature=v['temp'],  # Level of creativity in the response
                presence_penalty=v['presence'],  # penalize for tokens that are repetitive in responses
                frequency_penalty=v['frequency'],  # reduce likelihood of repetition from source
                prompt="Rewrite the following passage in the style of {}, with undertones of {}. "
                       "It should include {} spelling errors, and between {} words use double spaces. Include the following words: {}. Here is the passage: {}".format(
                    v['authors'], v['moods'], v['spellingErrors'], v['spacesErrors'], v['includeWords'], v['sourceML']),  # What the user typed in
                max_tokens=int(v['tokens']),  # Maximum tokens in the prompt AND response
                n=int(v['iterations']),  # The number of completions to generate
                stop=None,  # An optional setting to control response generation
            )

            print(curledSheets)
            chamberWindow['finalML'].update("\n{}".format(curledSheets.choices[0].text), append=True)

            if chamberWindow['generateImages']:
                print("Generate Images Set to True, Generating...")
                # for eachImage in range(0, v['generateImagesCount'])
                response2 = openai.Image.create(
                    prompt="{}".format(curledSheets.choices[0].text),
                    n=int(v['generateImagesCount']),
                    size="1024x1024",
                    response_format= "b64_json"
                    # TODO: Add input for custom additions for the image prompt - OFten the returned content is too long
                    # TODO: Check for 'too long' error, and add option to trim it down or provide custom prompt for image
                )

                for eachImage in range(1, int(v['generateImagesCount'] + 1)):
                    print(eachImage)
                    image_b64 = response2['data'][eachImage - 1]['b64_json']
                    # print(image_b64)
                    chamberWindow['image_{}'.format(eachImage)].update(data=image_b64, subsample=4)
                    # chamberWindow['imageColumn'].contents_changed()
                    # chamberWindow.refresh()
                    chamberWindow[f'image_{eachImage}'].bind("<Double-Button-1>", " Double")
                # TODO: Create a scrolling area to scroll through created and loaded images - New should pop to left
                # TODO: If you select the image, it should attribute itself to the page / chapter you're on
                # TODO: Selecting the image should insert code to load it during PDF/HTML generation

                    with open("savedBase64Images2.txt", "a+") as imageFile:
                        imageFile.write("{}\n\n".format(image_b64))

                chamberWindow['imageColumn'].contents_changed()
                chamberWindow.refresh()

            else:
                print("Generate Images Not Enabled, Bypassing...")



    def curlSheetsAgain(self):
        if self.connected:
            print("Cleaning Chamber...")
            curledSheets = openai.Completion.create(
                engine='text-davinci-003',  # Determines the quality, speed, and cost.
                temperature=v['temp'],  # Level of creativity in the response
                presence_penalty=v['presence'],  # penalize for tokens that are repetitive in responses
                frequency_penalty=v['frequency'],  # reduce likelihood of repetition from source
                prompt="Rewrite that again differently, add a bit of variation",  # What the user typed in
                max_tokens=int(v['tokens']),  # Maximum tokens in the prompt AND response
                n=int(v['iterations']),  # The number of completions to generate
                stop=None,  # An optional setting to control response generation
            )

            print(curledSheets)
            chamberWindow['finalML'].update("\n{}".format(curledSheets.choices[0].text), append=True)
        else:
            print("The Maid has not Arrived Yet...")

font1 = ('New Times Roman', 10)
font2 = ('New Times Roman', 48)

sg.set_options(font=font1)

class Photo(int):
    # Keep tk.Photoshop objects by index key to avoid memory leakage as same image used again and again.
    images = {}

    def __new__(cls, source=None, filename=None, data=None):
        """
        :param source:   A filename or a base64 bytes. Will automatically detect the type and fill in filename or data for you.
        :type source:    str | bytes | None
        :param filename: image filename if there is a button image. GIFs and PNGs only.
        :type filename:  str | None
        :param data:     Raw or Base64 representation of the image to put on button. Choose either filename or data
        :type data:      bytes | str | None
        """
        if source is not None:
            if isinstance(source, bytes):
                data = source
            elif isinstance(source, str):
                filename = source
            else:
                warnings.warn('Image element - source is not a valid type: {}'.format(type(source)), UserWarning)
        if filename is not None:
            photo = tk.PhotoImage(file=filename)
        elif data is not None:
            photo = tk.PhotoImage(data=data).subsample(4)


            # photo = photo.subsample(2)
        else:
            warnings.warn('No option of source for PhotoImage', UserWarning)
            return super().__new__(cls, -1)

        index = 0
        while index in Photo.images:
            index += 1
        Photo.images[index] = photo
        print(Photo.images[index])
        return  super().__new__(cls, index)

class Multiline(sg.Multiline):

    def image_create(self, index, key, align=None, padx=None, pady=None):
        """
        :param index: An index is a string used to indicate a particular place within a text, such as a place to insert characters or one endpoint of a range of characters to delete.
        :type index:  str
        :param key:   Specifies the key returned when Photo class initiated, image stored as Photo.images[key]
        :type key:    int
        :param align: If the image is not as tall as the line in which it is displayed, this option determines where the image is displayed in the line. Valid choices = 'top' (align the top of the image with the top of the line), 'center' (center the image within the range of the line), 'bottom' (align the bottom of the image with the bottom of the line's area) and 'baseline' (align the bottom of the image with the baseline of the line)
        :type align:  str | None
        :param padx:  Pixels specifies the amount of extra space to leave on each side of the embedded image.
        :type padx:   int | None
        :param pady:  Pixels specifies the amount of extra space to leave on the top and on the bottom of the embedded image.
        :type pady:   int | None
        :return:      A name unique to this instance of the image is returned. This name may then be used to refer to this image instance.
        :rtype:       (str)
        """
        if key in Photo.images:
            image = Photo.images[key]
            name = self.widget.image_create(index, align=align, image=image, padx=padx, pady=pady)
            return name

# TODO: Create PDF/HTML Gen
# TODO: Create Django backend / api to build out the books

dresser = [[sg.Column([[sg.Text("Organization ID:"), sg.InputText("Use Environment Variable 'chamberOrg", key = "org")],
                       [sg.Text("API Key           "), sg.InputText("Use Environment Variable 'chamberKey'")],
                       [sg.Button("Connect to API", key = "connect")]])]]

charBuilderLoadFrame = [[sg.Text("Character Name", size = (20,1), border_width=0), sg.InputText("")]]
charBuilder = [[
                # CHAR BUILDER TAB
                sg.Column([[sg.Column([[
                sg.Column([[

                sg.Frame("Load Character", charBuilderLoadFrame)
                ]])

                ]])

                ]])

                ]]

envBuilderLoadFrame = [[sg.Text("Environment Name", size = (20,1), border_width=0), sg.InputText("")]]

envBuilder = [[
                # CHAR BUILDER TAB
                sg.Column([[sg.Column([[
                sg.Column([[

                sg.Frame("Load Environment", envBuilderLoadFrame)
                ]])

                ]])

                ]])

                ]]
testObjectData = ["None", "Claudia", "Sarah", "Andrew"]

preface = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalMLpreface")]])]]
cover = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalMLcover")]])]]
introSynopsis = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalMLintroSynopsis")]])]]
chapterTab1 = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML")]])]]
chapterTab2 = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML2")]])]]
chapterTab3 = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML3")]])]]
chapterTab4 = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML4")]])]]
chapterTab5 = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML5")]])]]
chapterTab6 = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML6")]])]]
chapterTab7 = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML7")]])]]
chapterTab8 = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML8")]])]]
chapterTab9 = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML9")]])]]
chapterTab10 = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML10")]])]]
prologue = [[sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "prologue")]])]]

sheets = [[
                # MAIN TAB (API CONTROLS, SOURCE AND RETURNED DATA)
                sg.Column([[sg.Column([[
                sg.Column([[sg.Text("       Loaded Object")],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Author Reference", size = (20,1), border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Moods", size = (20,1), border_width=0)],
                # [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Reference Text", size = (20,1), border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Iterations", border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Rewrites", border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Include Words", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Exclude Words", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=False, disabled=True), sg.Text("Author Age", border_width=2, text_color="gray")],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Decent - Wild", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Presence", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Frequency", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Maximum Tokens", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Spelling Errors", border_width=1)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Spaces Errors", border_width=1)],[
                sg.Checkbox("", pad=(0,0), default=False), sg.Text("Append to Query", border_width=0)],[
                sg.Checkbox("Generate Response Images", pad=(0,0), default = True, key="generateImages")],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Session Wipe", border_width=0)
                           ]], element_justification="top", vertical_alignment="top"),

                # INPUTS
                sg.Column([[
                sg.DropDown(testObjectData, default_value="None")],
                [sg.DropDown(authorReferenceList, key = "authors", default_value="Anne Rice")],
                [sg.InputText("Nothing Specific", border_width=0, key = "moods")],
                # [sg.InputText("", border_width=0)],
                [sg.DropDown([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], default_value=1, key = "iterations")],
                [sg.DropDown([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], default_value=0, key = 'rewrites')],
                [sg.InputText("", border_width=0, key = "includeWords")],
                [sg.InputText("", border_width=0, key = "excludeWords")],
                [sg.Slider(default_value=33, range=(4, 103), size=(35, 6),
                           orientation="horizontal", border_width=0, pad=(0,0), key = "authorAge", disabled=True, text_color="gray")],
                [sg.Slider(default_value=1, range=(0.0, 2.0), size=(35, 6), resolution=.1,
                           orientation="horizontal", border_width=0, pad=(0,0), key = "temp")],

                [sg.Slider(default_value=0, range=(-2.0, 2.0), size=(35, 6), resolution=.1,
                                           orientation="horizontal", border_width=0, pad=(0,0), key = "presence")],
                [sg.Slider(default_value=0, range=(-2.0, 2.0), size=(35, 6), resolution=.1,
                                           orientation="horizontal", border_width=0, pad=(0,0), key = "frequency")],

                [sg.Slider(default_value=50, range=(1, 2048), size=(35, 6),
                           orientation="horizontal", border_width=0, pad=(0,0), key = "tokens")],
                [sg.DropDown(["No", "A few", "Some", "A lot of"], default_value="No", key = "spellingErrors")],
                [sg.DropDown(["No", "A few", "Some", "A lot of"], default_value="No", key = "spacesErrors")],
                [sg.InputText("Do not repeat exactly what I've written in the passage. Write it in an illustrious manner, add deep meaningful words but do not use the same meaningful word more than once..", border_width=0, key = "queryAppend")],
                [sg.Slider(default_value=1, range=(1, 6), size=(35,6), orientation="horizontal", key = "generateImagesCount")],
                [sg.Text("Curr:"), sg.Text("1234567890", key = "sessionID"), sg.Text("Wipe:"),
                 sg.DropDown(["1234567890", "0987654321", "123456098765", "1029384756"], default_value="1234567890", key = "sessionIDOverride")],
                []
                # TODO: Add button for creating a new chapter / and workflow to load and switch chapters and book titles
                           # TODO: Title and chapter should be a dropdown of historical saves - Load button loads the selection
                           ], vertical_alignment="top")], [sg.Multiline("", size=(74,10), key = "sourceML")],

                    [sg.Column([[sg.Image(key = "image_1", data=chamberPortraits.maid, subsample=4, enable_events=True),
                                 sg.Image(key = "image_2", data=chamberPortraits.unicorn, subsample=4, enable_events=True)],
                                 [sg.Image(key = "image_3", data=chamberPortraits.snails, subsample=4, enable_events=True),
                                  sg.Image(key = "image_4", data=chamberPortraits.snails, subsample=4, enable_events=True)],
                                [sg.Image(key = "image_5", data=chamberPortraits.snails, subsample=4, enable_events=True),
                                 sg.Image(key = "image_6", data=chamberPortraits.snails, subsample=4, enable_events=True)]], key="imageColumn", size=(524, 230), expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)
                ]], vertical_alignment="top"),

                sg.Column([[sg.TabGroup([[sg.Tab("Cover", cover),sg.Tab("Synopsis", introSynopsis), sg.Tab("Preface", preface), sg.Tab("Chapter 1", chapterTab1), sg.Tab("Chapter 2", chapterTab2), sg.Tab("Chapter 3", chapterTab3)
                                          , sg.Tab("Chapter 4", chapterTab4)
                                          , sg.Tab("Chapter 5", chapterTab5)
                                          , sg.Tab("Chapter 6", chapterTab6)
                                          , sg.Tab("Chapter 7", chapterTab7)
                                          , sg.Tab("Chapter 8", chapterTab8)
                                          , sg.Tab("Chapter 9", chapterTab9)
                                          , sg.Tab("Chapter 10", chapterTab10), sg.Tab("Prologue", prologue)]])],
                [sg.Text("Words/Pages/Images: 0000/0000/0000", justification="right")],[
                # sg.Column([[Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML")],[
                # sg.Text("Font Size:"), sg.Slider(default_value=12, range=(3, 22), orientation="horizontal",
                #                                 change_submits=True, key = "fontSize")
                ]])
                ]])],[

                # TODO: Add numbers to multiline, as well as image insertion

]]

topDrawer = [[sg.Column([[sg.Text("Title:"), sg.InputText("", border_width=0, size=(40,1)),
                          sg.Text("Chapter:"), sg.InputText("", size=(10,1), border_width=0), sg.Button("New Chapter", key = "newChapter", border_width=0),
                          sg.Button("Clean", key = "clean", border_width=0), sg.Button("Reclean", key = "Reclean", border_width=0),
                          sg.Button("Save", border_width=0), sg.Button("Load", border_width=0), sg.Button("Save Session", key = "ss", border_width=0),
                          sg.Button("Load Session", key="ls", border_width=0), sg.Button("Connect", key="connect", border_width=0),
                          sg.Checkbox("Save Concurrently", default=True, key="saveAll")]], element_justification="right", justification="left")]]

tabLayout = [[topDrawer, sg.TabGroup([[sg.Tab("Sheets", sheets), sg.Tab("Characters", charBuilder), sg.Tab("Environments", envBuilder)]])]]
chamberWindow = sg.Window(title = "Chamber Maid", layout = tabLayout, location = (0,0), border_depth=0, element_padding=1, finalize=True)

multiline = chamberWindow['finalML']

while True:
    b, v, = chamberWindow.Read()

    if b == "clean":
        maid.curlSheets()

    if b.startswith("image_1"):
        # index = int(b.split()[-1])
        # chamberWindow['finalML'].update("\n%__image_{}__%\n".format("IMAGE_B64_46572457283056"), append=True)
        # newB = str(b).replace(" Double", "")
        # print(chamberWindow[newB])

        # print(chamberWindow["image_1"].Data)
        photo = Photo(data=chamberWindow["image_1"].Data)
        # for align in (tk.TOP, tk.CENTER, tk.BOTTOM, tk.BASELINE):
            # multiline.update('Hello', append=True, font=font2)
            # """
            # The insert mark tk.INSERT represents the position of the insertion
            # cursor, and the insertion cursor will automatically be drawn at this
            # point whenever the text widget has the input focus.
            # """
        name = multiline.image_create(tk.INSERT, photo, padx=0)
            # multiline.update('World\n', append=True, font=font2)
    if b.startswith("image_2"):
        photo = Photo(data=chamberWindow["image_2"].Data)
        #for align in (tk.TOP, tk.CENTER, tk.BOTTOM, tk.BASELINE):
            # multiline.update('Hello', append=True, font=font2)
            # """
            # The insert mark tk.INSERT represents the position of the insertion
            # cursor, and the insertion cursor will automatically be drawn at this
            # point whenever the text widget has the input focus.
            # """
        name = multiline.image_create(tk.INSERT, photo, padx=0)
            # multiline.update('World\n', append=True, font=font2)
    if b.startswith("image_3"):
        photo = Photo(data=chamberWindow["image_3"].Data)
        # for align in (tk.TOP, tk.CENTER, tk.BOTTOM, tk.BASELINE):
        #     # multiline.update('Hello', append=True, font=font2)
        #     """
        #     The insert mark tk.INSERT represents the position of the insertion
        #     cursor, and the insertion cursor will automatically be drawn at this
        #     point whenever the text widget has the input focus.
        #     """
        name = multiline.image_create(tk.INSERT, photo, padx=0)
            # multiline.update('World\n', append=True, font=font2)

    if b == "Reclean":
        try:
            maid.curlSheetsAgain()
        except:
            print("The Maid has not Arrived Yet...")

    if b == "connect":
        maid = Maid(os.getenv("chamberKey"), os.getenv("chamberOrg"))
        maid.connect()
        # models = maid.listModels()
        # print(models)

    if b == "Save":
        with open("novelSave.txt", "a+") as novel:
            novel.write("\n\n{}".format(v['finalML']))

        with open("novelSource.txt", "a+") as source:
            source.write("\n\n{}".format(v['sourceML']))

    if b == "ss":
        with open("savedSession.txt", "w") as ss:
            ss.write("\n\n{}".format(v))

    if b == "ls":
        with open("savedSession.txt", "r") as readSS:
            save = readSS.readline()
            chamberWindow.refresh()

    if v == sg.WINDOW_CLOSED:
        break
