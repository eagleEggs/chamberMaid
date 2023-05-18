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

sg.theme("DarkGrey11")

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
                prompt="Please rewrite the following passage in the style of {}, and undertones of {}. "
                       "It should include {} spelling errors, and between {} words, use double spaces. Include the following words: {}. And write it as if the author is {} years old. Thanks. Here is the passage: {}".format(
                    v['authors'], v['moods'], v['spellingErrors'], v['spacesErrors'], v['includeWords'], v['authorAge'], v['sourceML']),  # What the user typed in
                max_tokens=int(v['tokens']),  # Maximum tokens in the prompt AND response
                n=int(v['iterations']),  # The number of completions to generate
                stop=None,  # An optional setting to control response generation
            )

            print(curledSheets)
            chamberWindow['finalML'].update("\n{}".format(curledSheets.choices[0].text), append=True)
        else:
            print("The Maid has not Arrived Yet...")

dresser = [[sg.Column([[sg.Text("Organization ID:"), sg.InputText("Use Environment Variable 'chamberOrg", key = "org")],
                       [sg.Text("API Key           "), sg.InputText("Use Environment Variable 'chamberKey'")],
                       [sg.Button("Connect to API", key = "connect")]])]]
sheets = [[
                # TEXTS
                sg.Column([[sg.Column([[
                sg.Column([[sg.Checkbox("", pad=(0,0), default=True), sg.Text("Author Reference", size = (20,1), border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Moods", size = (20,1), border_width=0)],
                # [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Reference Text", size = (20,1), border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Iterations", border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Rewrites", border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Include Words", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Author Age", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Decent - Wild", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Maximum Tokens", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Spelling Errors", border_width=1)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Spaces Errors", border_width=1)]], element_justification="top", vertical_alignment="top"),

                # INPUTS
                sg.Column([[sg.InputText("Oscar Wilde", border_width=0, key = "authors")],
                [sg.InputText("Dark, Sorrowful, and Despair", border_width=0, key = "moods")],
                # [sg.InputText("", border_width=0)],
                [sg.DropDown([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], default_value=1, key = "iterations")],
                [sg.DropDown([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], default_value=0, key = 'rewrites')],
                [sg.InputText("", border_width=0, key = "includeWords")],
                [sg.Slider(default_value=33, range=(4, 103), size=(35, 6),
                           orientation="horizontal", border_width=0, pad=(0,0), key = "authorAge")],
                [sg.Slider(default_value=0, range=(0, 2), size=(35, 6),
                           orientation="horizontal", border_width=0, pad=(0,0), key = "temp")],
                [sg.Slider(default_value=150, range=(1, 500), size=(35, 6),
                           orientation="horizontal", border_width=0, pad=(0,0), key = "tokens")],
                [sg.DropDown(["No", "A few", "Some", "A lot of"], default_value="No", key = "spellingErrors")],
                [sg.DropDown(["No", "A few", "Some", "A lot of"], default_value="False", key = "spacesErrors")],
                []

                           ], vertical_alignment="top")], [sg.Multiline("", size=(74,34), key = "sourceML")]], vertical_alignment="top"),


                sg.Column([[sg.Multiline("", size=(110, 50), border_width=0, pad=(0,0), key = "finalML")],[
                # sg.Text("Font Size:"), sg.Slider(default_value=12, range=(3, 22), orientation="horizontal",
                #                                 change_submits=True, key = "fontSize")
                ]])
                ]])],[


]]

topDrawer = [[sg.Column([[sg.Text("Title:"), sg.InputText(""), sg.Button("Clean", key = "clean"), sg.Button("Save"), sg.Button("Load")]], element_justification="right", justification="right")]]

tabLayout = [[topDrawer, sg.TabGroup([[sg.Tab("Sheets", sheets), sg.Tab("Dresser", dresser)]])]]
chamberWindow = sg.Window(title = "Chamber Maid", layout = tabLayout, location = (0,0), finalize=True)

while True:
    b, v, = chamberWindow.Read()

    if b == "clean":
        maid.curlSheets()

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

    if v == sg.WINDOW_CLOSED:
        break
