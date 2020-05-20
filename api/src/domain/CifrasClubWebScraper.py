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

    TOKEN_ARTIST_DASH_BAND_SPACE = 'Artist / Band: '
    TOKEN_SONG_NAME = 'Song name: '
    TOKEN_SONG_REF = 'Song href: '
    TOKEN_ERROR_MESSAGE = 'Error message: '

    def handleCommandList(self,commandList):
        commandList = commandList.copy()
        globals = self.globals
        apiKey = globals.CIFRAS_CLUB_WEB_SCRAPER
        if apiKey == commandList[0] :
            if len(commandList) > 1 :
                if 'revisit-failed-dataset' == commandList[1] :
                    try :
                        return self.revisitFailedDataSet()
                    except Exception as exception :
                        print(f'{globals.ERROR}{globals.apiName} Failed to run. Cause: {str(exception)}')
                        return
            else :
                try :
                    return self.scrapIt(commandList.remove(globals.CIFRAS_CLUB_WEB_SCRAPER))
                except Exception as exception :
                    print(f'{globals.ERROR}{globals.apiName} Failed to run. Cause: {str(exception)}')
                    return
        print(f'Missing: "{globals.CIFRAS_CLUB_WEB_SCRAPER}"')

    def __init__(self,globals,**kwargs):
        WebScrapHelper.WebScrapHelper.__init__(self,globals,**kwargs)

    def resetValues(self,url,artistName):
        self.url = url
        self.artistName = artistName

    def scrapIt(self,commandList):
        artistList = [
            'Led Zeppelin',
            'Metallica',
            'Bon Jovi',
            'U2',
            'Ramones',
            'John Mayer',
            "Guns N' Roses",
            'Mumford & Sons',
            'AC/DC',
            'Iron Maden'
        ]
        artistSet = {}
        for artistName in artistList :
            artistSet[artistName] = {}
        return self.getItScraped(artistSet)

    def getItScraped(self,artistSet):
        songLyricList = []
        songLineList = []
        secondSongLineList = []
        errorLineList = []
        for artistName in artistSet.keys() :
            self.resetValues(None,artistName)
            artistPage = self.accessArtist()
            artistSet[artistName] = self.getSongSet(artistPage).copy()
        return self.scrapSequence(artistSet)

    def scrapSequence(self,artistSet):
        songLyricList = []
        songLineList = []
        secondSongLineList = []
        errorLineList = []
        for artistName in artistSet.keys() :
            for songName,songHref in artistSet[artistName].items() :
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
        self.saveAll({
            f'{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{self.DATASET_FILE_NAME}.{self.globals.extension}' : songLineList,
            f'''{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{'second-dataset'}.{self.globals.extension}''' : secondSongLineList,
            f'{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{self.FAILED_DATASET_FILE_NAME}.{self.globals.extension}' : errorLineList
        })
        return songLyricList,songLineList,secondSongLineList,errorLineList

    def revisitFailedDataSet(self):
        dataSetFilePath = f'{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{self.FAILED_DATASET_FILE_NAME}.{self.globals.extension}'
        failedDataSet = self.getDataSetFile(dataSetFilePath)
        artistSet = {}
        for file in failedDataSet.split(self.SEPARATOR) :
            if file :
                lineList = file.split(self.globals.NEW_LINE)
                artistName = self.globals.NOTHING
                songName = self.globals.NOTHING
                songHref = self.globals.NOTHING
                for line in lineList :
                    if self.TOKEN_ARTIST_DASH_BAND_SPACE in line :
                        artistName = line.replace(self.TOKEN_ARTIST_DASH_BAND_SPACE,self.globals.NOTHING)
                    if self.TOKEN_SONG_NAME in line :
                        songName = line.replace(self.TOKEN_SONG_NAME,self.globals.NOTHING)
                    if self.TOKEN_SONG_REF in line :
                        songHref = line.replace(self.TOKEN_SONG_REF,self.globals.NOTHING)
                    if (not artistName == self.globals.NOTHING) and (not songName == self.globals.NOTHING) and (not songHref == self.globals.NOTHING) :
                        if artistName in artistSet.keys() :
                            artistSet[artistName][songName] = songHref
                        else :
                            artistSet[artistName] = {songName:songHref}
                        break
                break
        return self.scrapSequence(artistSet)


    def buildSongLines(self,artistName,songName,songHref,errorMessage,songLyric):
        return [
            self.SEPARATOR,
            self.globals.NOTHING,
            f'{self.TOKEN_ARTIST_DASH_BAND_SPACE}{artistName}',
            f'{self.TOKEN_SONG_NAME}{songName}',
            f'{self.TOKEN_SONG_REF}{songHref}',
            f'{self.TOKEN_ERROR_MESSAGE}{errorMessage.replace(self.globals.NEW_LINE,self.globals.NOTHING)}',
            self.globals.NOTHING,
            self.START_OF_TEXT,
            songLyric,
            self.END_OF_TEXT,
            self.globals.NOTHING
        ]

    def getDataSetFile(self,dataSetFilePath):
        file = ''
        with open(dataSetFilePath,self.globals.READ,encoding = self.globals.ENCODING) as dataSetFile :
            file = self.globals.NOTHING.join(dataSetFile.readlines())
        return file

    def saveAll(self,dataSetSet):
        for dataSetPath,dataSetLineList in dataSetSet.items() :
            self.saveDataSetFile(dataSetLineList,dataSetPath)

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
