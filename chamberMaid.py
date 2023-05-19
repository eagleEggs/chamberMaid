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

authorReferenceList = ["Oscar Wilde", "Anne Rice", "Nathaniel Hawthorne", "Stephen King", "Voltaire", "C.S. Lewis",
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
                prompt="Rewrite the following passage in the style of {}, with undertones of {}. "
                       "It should include {} spelling errors, and between {} words use double spaces. Include the following words: {}. Here is the passage: {}".format(
                    v['authors'], v['moods'], v['spellingErrors'], v['spacesErrors'], v['includeWords'], v['sourceML']),  # What the user typed in
                max_tokens=int(v['tokens']),  # Maximum tokens in the prompt AND response
                n=int(v['iterations']),  # The number of completions to generate
                stop=None,  # An optional setting to control response generation
            )

            print(curledSheets)
            chamberWindow['finalML'].update("\n{}".format(curledSheets.choices[0].text), append=True)

            if v['generateImages']:
                response = openai.Image.create(
                    prompt="{}".format(curledSheets.choices[0].text),
                    n=v['generateImagesCount'],
                    size="1024x1024",
                    response_format= "b64_json"
                )
                image_b64 = response['data'][0]

        else:
            print("The Maid has not Arrived Yet...")

    def curlSheetsAgain(self):
        if self.connected:
            print("Cleaning Chamber...")
            curledSheets = openai.Completion.create(
                engine='text-davinci-003',  # Determines the quality, speed, and cost.
                temperature=v['temp'],  # Level of creativity in the response
                prompt="Rewrite that again differently, add a bit of variation",  # What the user typed in
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
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Exclude Words", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=False, disabled=True), sg.Text("Author Age", border_width=2, text_color="gray")],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Decent - Wild", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Maximum Tokens", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Spelling Errors", border_width=1)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Spaces Errors", border_width=1)],[
                sg.Checkbox("", pad=(0,0), default=False), sg.Text("Append to Query", border_width=0)],[
                sg.Checkbox("Generate Response Images", pad=(0,0), default = False, key="generateImages")
                           ]], element_justification="top", vertical_alignment="top"),

                # INPUTS
                sg.Column([[sg.DropDown(authorReferenceList, key = "authors", default_value="Anne Rice")],
                [sg.InputText("Dark, Sorrowful, and Despair", border_width=0, key = "moods")],
                # [sg.InputText("", border_width=0)],
                [sg.DropDown([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], default_value=1, key = "iterations")],
                [sg.DropDown([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], default_value=0, key = 'rewrites')],
                [sg.InputText("", border_width=0, key = "includeWords")],
                [sg.InputText("", border_width=0, key = "excludeWords")],
                [sg.Slider(default_value=33, range=(4, 103), size=(35, 6),
                           orientation="horizontal", border_width=0, pad=(0,0), key = "authorAge", disabled=True, text_color="gray")],
                [sg.Slider(default_value=1, range=(0, 2), size=(35, 6),
                           orientation="horizontal", border_width=0, pad=(0,0), key = "temp")],
                [sg.Slider(default_value=150, range=(1, 500), size=(35, 6),
                           orientation="horizontal", border_width=0, pad=(0,0), key = "tokens")],
                [sg.DropDown(["No", "A few", "Some", "A lot of"], default_value="No", key = "spellingErrors")],
                [sg.DropDown(["No", "A few", "Some", "A lot of"], default_value="No", key = "spacesErrors")],
                [sg.InputText("Do not repeat exactly what I've written in the passage. Write it in an illustrious manner, add deep meaningful words but do not use the same meaningful word more than once..", border_width=0, key = "queryAppend")],
                [sg.Slider(default_value=1, range=(1, 10), size=(35,6), orientation="horizontal", key = "generateImagesCount")],
                []

                           ], vertical_alignment="top")], [sg.Multiline("", size=(74,34), key = "sourceML")]], vertical_alignment="top"),


                sg.Column([[sg.Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML")],[
                # sg.Text("Font Size:"), sg.Slider(default_value=12, range=(3, 22), orientation="horizontal",
                #                                 change_submits=True, key = "fontSize")
                ]])
                ]])],[


]]

topDrawer = [[sg.Column([[sg.Text("Title:"), sg.InputText(""), sg.Button("Clean", key = "clean"), sg.Button("Reclean", key = "Reclean"),sg.Button("Save"), sg.Button("Load"), sg.Button("Save Session", key = "ss"), sg.Button("Load Session", key="ls"), sg.Button("Connect", key="connect")]], element_justification="right", justification="right")]]

tabLayout = [[topDrawer, sg.TabGroup([[sg.Tab("Sheets", sheets)]])]]
chamberWindow = sg.Window(title = "Chamber Maid", layout = tabLayout, location = (0,0), finalize=True)

while True:
    b, v, = chamberWindow.Read()

    if b == "clean":
        try:
            maid.curlSheets()
        except:
            print("The Maid has not Arrived Yet...")

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
