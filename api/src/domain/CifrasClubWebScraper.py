import WebScrapHelper

class CifrasClubWebScraper(WebScrapHelper.WebScrapHelper):

    CONTEXT_DATA_T_ARTIST = f'//a[@data-t="artist"]'

    PAGE_SONG_BODY = 'js-w-content'
    CLASS_ARTIST_LINK = 'art_music-link'
    CLASS_LETRA_L = 'letra-l'
    CLASS_LETRA = 'letra'

    START_OF_TEXT = '<|startoftext|>'
    END_OF_TEXT = '<|endoftext|>'
    LINE_SEPARATOR = '==================================================================================================================================================================================='
    SEPARATOR = f'{LINE_SEPARATOR}\n{LINE_SEPARATOR}\n{LINE_SEPARATOR}'

    def handleCommandList(self,commandList):
        try :
            commandList = commandList.copy()
            globals = self.globals
            apiKey = globals.CIFRAS_CLUB_WEB_SCRAPER
            if apiKey == commandList[0] :
                return self.scrapIt(commandList.remove(globals.CIFRAS_CLUB_WEB_SCRAPER))
            print(f'Missing: "{globals.CIFRAS_CLUB_WEB_SCRAPER}"')
        except Exception as exception :
            print(f'{globals.ERROR}{globals.apiName} Failed to run. Cause: {str(exception)}')

    def __init__(self,globals,**kwargs):
        WebScrapHelper.WebScrapHelper.__init__(self,globals,**kwargs)

    def resetValues(self,url,artistName):
        self.url = url
        self.artistName = artistName

    def scrapIt(self,commandList):
        artistList = [
            'Ramones',
            'John Mayer',
            "Guns N' Roses",
            'Mumford & Sons',
            'AC/DC'
        ]
        songLyricList = []
        songLineList = []
        secondSongLineList = []
        errorLineList = []
        for artistName in artistList :
            self.resetValues(None,artistName)
            artistPage = self.accessArtist()
            songSet = self.getSongSet(artistPage).copy()
            for songName,songHref in songSet.items() :
                try :
                    print()
                    print(f'Scrapping {songName} song from {songHref}')
                    songPage = self.accessSong(songHref)
                    songLyric, errorMessage = self.getSongLyric(songPage)
                    songLyricList.append(songLyric)
                    if errorMessage :
                        secondSongLineList += self.buildSongLines(artistName,songName,songHref,errorMessage,songLyric)
                    else :
                        songLineList += self.buildSongLines(artistName,songName,songHref,errorMessage,songLyric)
                    print('Success!')
                except Exception as exception :
                    errorMessage = f'{self.globals.ERROR}Not possible to scrap {songName} from {songHref}. Cause: {str(exception)}'
                    songLyric = ''
                    errorLineList += self.buildSongLines(artistName,songName,songHref,errorMessage,'')
                    print(errorMessage)
                print()
        self.saveDataSetFile(songLineList,f'{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{self.DATASET_FILE_NAME}.{self.globals.extension}')
        self.saveDataSetFile(secondSongLineList,f'''{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{'second-dataset'}.{self.globals.extension}''')
        self.saveDataSetFile(errorLineList,f'{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{self.FAILED_DATASET_FILE_NAME}.{self.globals.extension}')
        return songLyricList
        # dataSetFilePath = f'{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{self.DATASET_FILE_NAME}.{self.globals.extension}'
        # with open(dataSetFilePath,self.globals.OVERRIDE,encoding = self.globals.ENCODING) as dataSetFile :
        #     dataSetFile.write(self.globals.NEW_LINE.join(songLineList))

        # secondDataSetFilePath = f'{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{self.DATASET_FILE_NAME}.{self.globals.extension}'
        # with open(secondDataSetFilePath,self.globals.OVERRIDE,encoding = self.globals.ENCODING) as secondDataSetFile :
        #     secondDataSetFile.write(self.globals.NEW_LINE.join(secondSongLineList))

        # failedDataSetFilePath = f'{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{self.FAILED_DATASET_FILE_NAME}.{self.globals.extension}'
        # with open(failedDataSetFilePath,self.globals.OVERRIDE,encoding = self.globals.ENCODING) as failedDataSetFile :
        #     failedDataSetFile.write(self.globals.NEW_LINE.join(errorLineList))

    def buildSongLines(self,artistName,songName,songHref,errorMessage,songLyric):
        return [
            self.SEPARATOR,
            '',
            f'Artist / Band: {artistName}',
            f'Song name: {songName}',
            f'Song href: {songHref}',
            f'Error message: {errorMessage.replace(self.globals.NEW_LINE,self.globals.NOTHING)}',
            f'',
            self.START_OF_TEXT,
            songLyric,
            self.END_OF_TEXT,
            ''
        ]

    def saveDataSetFile(self,dataSetLineList,dataSetFilePath):
        with open(dataSetFilePath,self.globals.OVERRIDE,encoding = self.globals.ENCODING) as dataSetFile :
            dataSetFile.write(self.globals.NEW_LINE.join(dataSetLineList))

    def accessArtist(self):
        return self.accessUrl(f'''{self.mainUrl}{self.artistName.strip().lower().replace('`','').replace("'",'').replace("'",'').replace(' &','').replace(' / ',' ').replace(' /',' ').replace('/ ',' ').replace('/',' ').replace(' ','-')}{'/'}''')

    def search(self,driver):
        inputElement = self.findByTag(self.TAG_IMPUT,self.findByTag(self.TAG_FORM,self.findByTag(self.TAG_HEADER,driver)))
        inputElement = self.typeIn(self.textSearch,inputElement)

    def hitArtist(self,searchPage):
        return self.findBySelector(self.SELECTOR_DATA_T_ARTIST,searchPage)

    def getSongSet(self,artistPage):
        songLineList = self.findAllByClass(CifrasClubWebScraper.CLASS_ARTIST_LINK,artistPage)
        songSet = {}
        for song in songLineList :
            songSet[song.text] = song.get_attribute(self.ATTRIBUTE_HREF)
        return songSet

    def accessSong(self,href):
        self.newDriver()
        return self.accessUrl(href)

    def getSongLyric(self,songPage):
        songPageBody = self.findById(self.PAGE_SONG_BODY,songPage)
        errorMessage = ''
        try :
            return self.findByTag(self.TAG_PRE,songPageBody).text, errorMessage
        except Exception as exception :
            errorMessage += f'{self.globals.apiName} Failed to access tag {self.TAG_PRE}. Cause: {str(exception)}'
            self.globals.debug(errorMessage)
            try :
                return self.findByClass(self.CLASS_LETRA_L,songPageBody).text, f'{self.globals.ERROR}{errorMessage}'
            except Exception as exception :
                newErrorMessage = f'{self.globals.apiName} Failed to access css class {self.CLASS_LETRA_L}. Cause: {str(exception)}'
                self.globals.debug(newErrorMessage)
                errorMessage += f'{self.globals.SPACE_DASH_SPACE}{newErrorMessage}'
                try :
                    return self.findByClass(self.CLASS_LETRA,songPageBody).text, f'{self.globals.ERROR}{errorMessage}'
                except Exception as exception :
                    newErrorMessage = f'{self.globals.apiName} Failed to access css class {self.CLASS_LETRA}. Cause: {str(exception)}'
                    self.globals.debug(newErrorMessage)
                    errorMessage += f'{self.globals.SPACE_DASH_SPACE}{newErrorMessage}'
                    return '', f'{self.globals.ERROR}{errorMessage}'
