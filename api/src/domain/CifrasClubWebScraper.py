import WebScrapHelper

class CifrasClubWebScraper(WebScrapHelper.WebScrapHelper):

    CONTEXT_DATA_T_ARTIST = f'//a[@data-t="artist"]'

    PAGE_SONG_BODY = 'js-w-content'
    CLASS_ARTIST_LINK = 'art_music-link'

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
        self.resetValues(None,'John Mayer')
        artistPage = self.accessArtist()
        songNameList = self.getSongNameList(artistPage)
        print(f'songNameList = {songNameList}')
        songLyricList = []
        for songName in songNameList :
            songPage = self.accessSong(songName)
            songLyric = self.getSongLyric(songPage)
            songLyricList.append(songLyric)
            print(songLyric)
            break
        return songLyricList

    def accessArtist(self):
        return self.accessUrl(f'''{self.mainUrl}{self.artistName.strip().lower().replace(' ','-')}{'/'}''')

    def search(self,driver):
        inputElement = self.findByTag(self.TAG_IMPUT,self.findByTag(self.TAG_FORM,self.findByTag(self.TAG_HEADER,driver)))
        inputElement = self.typeIn(self.textSearch,inputElement)

    def hitArtist(self,searchPage):
        return self.findBySelector(self.SELECTOR_DATA_T_ARTIST,searchPage)

    def getSongNameList(self,artistPage):
        songElementList = self.findAllByClass(CifrasClubWebScraper.CLASS_ARTIST_LINK,artistPage)
        songNameList = []
        for song in songElementList :
            songNameList.append(song.text)
        return songNameList

    def accessSong(self,songName):
        return self.accessUrl(f'''{self.mainUrl}{self.artistName.strip().lower().replace(' ','-')}{'/'}{songName.strip().lower().replace(' ','-')}''')

    def getSongLyric(self,songPage):
        songPageBody = self.findById(self.PAGE_SONG_BODY,songPage)
        songLyricElement = self.findByTag(self.TAG_PRE,songPageBody)
        return songLyricElement.text
