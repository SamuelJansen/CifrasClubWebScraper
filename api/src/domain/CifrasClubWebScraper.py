import WebScrapHelper

class CifrasClubWebScraper(WebScrapHelper.WebScrapHelper):

    CONTEXT_DATA_T_ARTIST = f'//a[@data-t="artist"]'

    PAGE_SONG_BODY = 'js-w-content'
    CLASS_ARTIST_LINK = 'art_music-link'
    CLASS_LETRA_L = 'letra-l'
    CLASS_LETRA = 'letra'

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
        for artistName in artistList :
            self.resetValues(None,artistName)
            artistPage = self.accessArtist()
            songSet = self.getSongSet(artistPage).copy()
            songList = []
            songLyricList = []
            errorMessageList = []
            for songName,songHref in songSet.items() :
                try :
                    print()
                    print(f'Scrapping {songName} song from {songHref}')
                    songPage = self.accessSong(songHref)
                    songLyric = self.getSongLyric(songPage)
                    songLyricList.append(songLyric)
                    songList += [
                        '<|startoftext|>',
                        f'Song name: {songName}',
                        f'Song href: {songHref}',
                        f'Song lyric: {songLyric}',
                        '<|endoftext|>'
                    ]
                    print('Success!')
                except Exception as exception :
                    errorMessage = f'{self.globals.ERROR}Not possible to scrap {songName} from {songHref}. Cause: {str(exception)}'
                    errorMessageList += [
                        '<|startoftext|>',
                        f'Song name: {songName}',
                        f'Song href: {songHref}',
                        f'Song lyric: {errorMessage}',
                        '<|endoftext|>'
                    ]
                    print(errorMessage)
                print()
        dataSetFilePath = f'{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{self.DATASET_FILE_NAME}.{self.globals.extension}'
        with open(dataSetFilePath,self.globals.OVERRIDE,encoding = self.globals.ENCODING) as dataSetFile :
            dataSetFile.write(self.globals.NEW_LINE.join(songList))
        failedDataSetFilePath = f'{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{self.FAILED_DATASET_FILE_NAME}.{self.globals.extension}'
        with open(failedDataSetFilePath,self.globals.OVERRIDE,encoding = self.globals.ENCODING) as failedDataSetFile :
            failedDataSetFile.write(self.globals.NEW_LINE.join(errorMessageList))
        return songLyricList

    def accessArtist(self):
        return self.accessUrl(f'''{self.mainUrl}{self.artistName.strip().lower().replace('`','').replace("'",'').replace("'",'').replace(' &','').replace(' / ',' ').replace(' /',' ').replace('/ ',' ').replace('/',' ').replace(' ','-')}{'/'}''')

    def search(self,driver):
        inputElement = self.findByTag(self.TAG_IMPUT,self.findByTag(self.TAG_FORM,self.findByTag(self.TAG_HEADER,driver)))
        inputElement = self.typeIn(self.textSearch,inputElement)

    def hitArtist(self,searchPage):
        return self.findBySelector(self.SELECTOR_DATA_T_ARTIST,searchPage)

    def getSongSet(self,artistPage):
        songList = self.findAllByClass(CifrasClubWebScraper.CLASS_ARTIST_LINK,artistPage)
        songSet = {}
        for song in songList :
            songSet[song.text] = song.get_attribute(self.ATTRIBUTE_HREF)
        return songSet

    def accessSong(self,href):
        self.newDriver()
        return self.accessUrl(href)

    def getSongLyric(self,songPage):
        songPageBody = self.findById(self.PAGE_SONG_BODY,songPage)
        try :
            songLyricElement = self.findByTag(self.TAG_PRE,songPageBody)
            return songLyricElement.text
        except Exception as exception :
            errorMessage = f'{self.globals.apiName} Failed to access tag {self.TAG_PRE}. Cause: {str(exception)}'
            self.globals.debug(errorMessage)
            try :
                songLyricElement = self.findByClass(self.CLASS_LETRA_L,songPageBody)
                return f'{self.globals.ERROR}{errorMessage}{self.globals.NEW_LINE}{songLyricElement.text}'
            except Exception as exception :
                newErrorMessage = f'{self.globals.apiName} Failed to access css class {self.CLASS_LETRA_L}. Cause: {str(exception)}'
                errorMessage += f'{self.globals.SPACE_DASH_SPACE}{newErrorMessage}'
                self.globals.debug(newErrorMessage)
                try :
                    songLyricElement = self.findByClass(self.CLASS_LETRA,songPageBody)
                    return f'{self.globals.ERROR}{errorMessage}{self.globals.NEW_LINE}{songLyricElement.text}'
                except Exception as exception :
                    newErrorMessage = f'{self.globals.apiName} Failed to access css class {self.CLASS_LETRA}. Cause: {str(exception)}'
                    errorMessage += f'{self.globals.SPACE_DASH_SPACE}{newErrorMessage}'
                    self.globals.debug(newErrorMessage)
                    return f'{self.globals.ERROR}{errorMessage}{self.globals.NEW_LINE}{songLyricElement.text}'
