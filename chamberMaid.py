######################################################################################################  chamberMaid v0.1
########################################################################################################################

# IMPORTS
import PySimpleGUI
import openai
import dill
import os
import uuid
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

    def connect(self):
        openai.organization = "{}".format(self.org)
        openai.api_key = os.getenv("{}".format(self.APIKey))

    def listModels(self):
        modelList = openai.Model.list()
        return modelList

dresser = [[sg.Column([[sg.Text("Organization ID:"), sg.InputText("")],
                       [sg.Text("API Key           "), sg.InputText("")],
                       [sg.Button("Connect to API")]])]]
sheets = [[
                # TEXTS
                sg.Column([[sg.Column([[
                sg.Column([[sg.Checkbox("", pad=(0,0), default=True), sg.Text("Author Reference", size = (20,1), border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Moods", size = (20,1), border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=True), sg.Text("Reference Text", size = (20,1), border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Iterations", border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Rewrites", border_width=0)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Include Words", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Author Age", border_width=2)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Spelling Errors", border_width=1)],
                [sg.Checkbox("", pad=(0,0), default=False), sg.Text("Spaces Errors", border_width=1)]], element_justification="top", vertical_alignment="top"),

                # INPUTS
                sg.Column([[sg.InputText("Oscar Wilde", border_width=0)],
                [sg.InputText("Dark, Sorrowful, Despair", border_width=0)],
                [sg.InputText("", border_width=0)],
                [sg.DropDown([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], default_value=0)],
                [sg.DropDown([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], default_value=0)],
                [sg.InputText("", border_width=0)],
                [sg.Slider(default_value=33, range=(4, 103), size=(35, 6), orientation="horizontal", border_width=0, pad=(0,0))],
                [sg.DropDown(["True", "False"], default_value="False")],
                [sg.DropDown(["True", "False"], default_value="False")],
                []

                           ], vertical_alignment="top")], [sg.Multiline("", size=(74,35))]], vertical_alignment="top"),


                sg.Column([[sg.Multiline("", size=(100, 50), border_width=0, pad=(0,0))]])
                ]])],[


]]

topDrawer = [[sg.Column([[sg.Text("Title:"), sg.InputText(""), sg.Button("Clean"), sg.Button("Save"), sg.Button("Load")]], element_justification="right", justification="right")]]

tabLayout = [[topDrawer, sg.TabGroup([[sg.Tab("Sheets", sheets), sg.Tab("Dresser", dresser)]])]]
chamberWindow = sg.Window(title = "Chamber Maid", layout = tabLayout, location = (0,0), finalize=True)

while True:
    b, v, = chamberWindow.Read()

    if v == sg.WINDOW_CLOSED:
        break
