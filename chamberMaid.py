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
            # TODO: Create a scrolling area to scroll through created and loaded images - New should pop to left
            # TODO: If you select the image, it should attribute itself to the page / chapter you're on
            # TODO: Selecting the image should insert code to load it during PDF/HTML generation

                with open("savedBase64Images2.txt", "a+") as imageFile:
                    imageFile.write("{}\n\n".format(image_b64))

            chamberWindow['imageColumn'].contents_changed()
            chamberWindow.refresh()



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
                sg.Checkbox("Generate Response Images", pad=(0,0), default = True, key="generateImages")
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

                [sg.Slider(default_value=150, range=(1, 2048), size=(35, 6),
                           orientation="horizontal", border_width=0, pad=(0,0), key = "tokens")],
                [sg.DropDown(["No", "A few", "Some", "A lot of"], default_value="No", key = "spellingErrors")],
                [sg.DropDown(["No", "A few", "Some", "A lot of"], default_value="No", key = "spacesErrors")],
                [sg.InputText("Do not repeat exactly what I've written in the passage. Write it in an illustrious manner, add deep meaningful words but do not use the same meaningful word more than once..", border_width=0, key = "queryAppend")],
                [sg.Slider(default_value=1, range=(1, 3), size=(35,6), orientation="horizontal", key = "generateImagesCount")],
                []
                # TODO: Add button for creating a new chapter / and workflow to load and switch chapters and book titles
                           # TODO: Title and chapter should be a dropdown of historical saves - Load button loads the selection
                           ], vertical_alignment="top")], [sg.Multiline("", size=(74,10), key = "sourceML")],

                    [sg.Column([[sg.Image(key = "image_1", size = (5,5), data="", subsample=4),
                                 sg.Image(key = "image_2", size = (5,5), data="", subsample=4),
                                 sg.Image(key = "image_3", size = (5,5), data="", subsample=4)]], key="imageColumn", size=(524, 230), expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=False)
                ]], vertical_alignment="top"),


                sg.Column([[sg.Multiline("", size=(130, 52), border_width=0, pad=(0,0), key = "finalML")],[
                # sg.Text("Font Size:"), sg.Slider(default_value=12, range=(3, 22), orientation="horizontal",
                #                                 change_submits=True, key = "fontSize")
                ]])
                ]])],[


]]

topDrawer = [[sg.Column([[sg.Text("Title:"), sg.InputText("", border_width=0, size=(40,1)),
                          sg.Text("Chapter:"), sg.InputText("", size=(10,1), border_width=0), sg.Button("New Chapter", key = "newChapter", border_width=0),
                          sg.Button("Clean", key = "clean", border_width=0), sg.Button("Reclean", key = "Reclean", border_width=0),
                          sg.Button("Save", border_width=0), sg.Button("Load", border_width=0), sg.Button("Save Session", key = "ss", border_width=0),
                          sg.Button("Load Session", key="ls", border_width=0), sg.Button("Connect", key="connect", border_width=0),
                          sg.Checkbox("Save Concurrently", default=True, key="saveAll")]], element_justification="right", justification="left")]]

tabLayout = [[topDrawer, sg.TabGroup([[sg.Tab("Sheets", sheets), sg.Tab("Characters", charBuilder), sg.Tab("Environments", envBuilder)]])]]
chamberWindow = sg.Window(title = "Chamber Maid", layout = tabLayout, location = (0,0), finalize=True)

while True:
    b, v, = chamberWindow.Read()

    if b == "clean":

        maid.curlSheets()


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
