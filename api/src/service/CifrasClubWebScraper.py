import WebScrapHelper, OriginalContent
from CifrasClubTable import *

import OriginalContent
OriginalContent = OriginalContent.OriginalContent

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

    TOKEN_PERFORMER_DASH_BAND_SPACE = 'Performer: '
    TOKEN_SONG_NAME = 'Song name: '
    TOKEN_SONG_REF = 'Song href: '
    TOKEN_ERROR_MESSAGE = 'Error message: '

    KW_SCRAP = 'scrap'
    KW_REVISIT_FAILED_DATASET = 'revisit-failed-dataset'
    KW_QUERY = 'query'

    def __init__(self,globals,**kwargs):
        kwargs['model'] = Model
        WebScrapHelper.WebScrapHelper.__init__(self,globals,**kwargs)
        self.commandSet = {
            self.KW_SCRAP : self.scrapIt,
            self.KW_QUERY : self.queryIt,
            self.KW_REVISIT_FAILED_DATASET : self.revisitIt
        }

    def resetValues(self,url,performerName):
        self.url = url
        self.performerName = performerName

    def scrapIt(self,performerList):
        globals = self.globals
        self.newDriver()
        print(f'Scraping performers = {performerList}')
        if performerList :
            try :
                performerSet = {}
                for performerName in performerList :
                    performerSet[performerName] = {}
                return self.getItScraped(performerSet)
            except Exception as exception :
                print(f'{globals.ERROR}{globals.apiName} Failed to scrap it {performerList}. Cause: {str(exception)}')
                return
        print(f'Missing performer list')

    def queryIt(self,queryList):
        print(f'queryList = {queryList}')
        if queryList :
            try :
                query = {}
                try :
                    performerName = queryList[0]
                    if performerName != self.globals.NOTHING :
                        query['performer'] = performerName
                except : pass
                try :
                    songName = queryList[1]
                    if songName != self.globals.NOTHING :
                        query['name'] = songName
                except : pass
                return self.repository.findAllByQuery(query,OriginalContent)
                # return self.repository.session.query(OriginalContent).filter_by(name=songName).all()
            except Exception as exception :
                print(f'{globals.ERROR}{globals.apiName} Failed to query it {queryList}. Cause: {str(exception)}')
                return
        print(f'Missing performer list')

    def revisitIt(self,revisitList):
        self.newDriver()
        try :
            return self.revisitFailedDataSet()
        except Exception as exception :
            print(f'{globals.ERROR}{globals.apiName} Failed to run. Cause: {str(exception)}')
            return

    def getItScraped(self,performerSet):
        songLyricList = []
        songLineList = []
        secondSongLineList = []
        errorLineList = []
        for performerName in performerSet.keys() :
            self.resetValues(None,performerName)
            performerPage = self.accessPerformer()
            performerSet[performerName] = self.getSongSet(performerPage).copy()
        return self.scrapSequence(performerSet)

    def scrapSequence(self,performerSet):
        songLyricList = []
        songLineList = []
        secondSongLineList = []
        errorLineList = []
        for performerName in performerSet.keys() :
            for songName,songHref in performerSet[performerName].items() :
                try :
                    print()
                    print(f'Scrapping {songName} song from {songHref}')
                    songPage = self.accessSong(songHref)
                    songLyric, errorMessage = self.getSongLyric(songPage)
                    songLyricList.append(songLyric)
                    if errorMessage :
                        secondSongLineList += self.buildSongLines(performerName,songName,songHref,errorMessage,songLyric)
                    else :
                        songLineList += self.buildSongLines(performerName,songName,songHref,errorMessage,songLyric)
                    print('Success!')
                except Exception as exception :
                    errorMessage = f'{self.globals.ERROR}Not possible to scrap {songName} from {songHref}. Cause: {str(exception)}'
                    songLyric = ''
                    errorLineList += self.buildSongLines(performerName,songName,songHref,errorMessage,'')
                    print(errorMessage)
                print()
        self.saveAll({
            self.buildRepositoryFilePath(self.DATASET_FILE_NAME) : songLineList,
            self.buildRepositoryFilePath(self.SECOND_DATASET_FILE_NAME) : secondSongLineList,
            self.buildRepositoryFilePath(self.FAILED_DATASET_FILE_NAME) : errorLineList
        })
        return songLyricList,songLineList,secondSongLineList,errorLineList

    def buildRepositoryFilePath(self,fileName):
        return f'''{self.globals.apiPath}{self.globals.baseApiPath}{self.FILE_FOLDER_LOCAL_PATH}{fileName}.{self.globals.extension}'''

    def revisitFailedDataSet(self):
        dataSetFilePath = f'{self.globals.apiPath}{self.globals.baseApiPath}{self.globals.REPOSITORY_BACK_SLASH}{self.FAILED_DATASET_FILE_NAME}.{self.globals.extension}'
        failedDataSet = self.getDataSetFile(dataSetFilePath)
        performerSet = {}
        for file in failedDataSet.split(self.SEPARATOR) :
            if file :
                lineList = file.split(self.globals.NEW_LINE)
                performerName = self.globals.NOTHING
                songName = self.globals.NOTHING
                songHref = self.globals.NOTHING
                for line in lineList :
                    if self.TOKEN_PERFORMER_DASH_BAND_SPACE in line :
                        performerName = line.replace(self.TOKEN_PERFORMER_DASH_BAND_SPACE,self.globals.NOTHING)
                    if self.TOKEN_SONG_NAME in line :
                        songName = line.replace(self.TOKEN_SONG_NAME,self.globals.NOTHING)
                    if self.TOKEN_SONG_REF in line :
                        songHref = line.replace(self.TOKEN_SONG_REF,self.globals.NOTHING)
                    if (not performerName == self.globals.NOTHING) and (not songName == self.globals.NOTHING) and (not songHref == self.globals.NOTHING) :
                        if performerName in performerSet.keys() :
                            performerSet[performerName][songName] = songHref
                        else :
                            performerSet[performerName] = {songName:songHref}
                        break
                break
        return self.scrapSequence(performerSet)


    def buildSongLines(self,performerName,songName,songHref,errorMessage,songLyric):
        try :
            if len(songLyric) >= 32768 :
                songLyric = songLyric[:32768]
            originalContent = OriginalContent(performerName,songName,songHref,songLyric)
            self.repository.session.add(originalContent)
            self.repository.session.commit()
        except Exception as exception :
            exceptionMessage = str(exception)
            self.repository.session.expire_all()
            try :
                self.repository.session.close()
                self.repository.session.begin()
            except Exception as exception :
                print(f'{self.globals.ERROR}Not possible to restart session. Cause: {str(exception)}')
            print(f'{self.globals.ERROR}Not possible to scrap {songName} from {songHref}. Cause: {exceptionMessage}')
        return [
            self.SEPARATOR,
            self.globals.NOTHING,
            f'{self.TOKEN_PERFORMER_DASH_BAND_SPACE}{performerName}',
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

    def accessPerformer(self):
        filteredPerformName = self.removeCharactere(self.performerName.strip().lower(),'`')
        filteredPerformName = self.removeCharactere(filteredPerformName,"'")
        filteredPerformName = self.removeCharactere(filteredPerformName,'"')
        filteredPerformName = self.removeCharactere(filteredPerformName,'&')
        filteredPerformName = self.removeCharactere(filteredPerformName,' / ')
        filteredPerformName = self.removeCharactere(filteredPerformName,'&')
        return self.accessUrl(f'''{self.mainUrl}{filteredPerformName.replace(' ','-')}{'/'}''')

    def removeCharactere(self,string,characterer):
        return string.replace(f' {characterer} ',' ').replace(f' {characterer}',' ').replace(f'{characterer} ',' ').replace(f'{characterer}',' ')

    def search(self,driver):
        inputElement = self.findByTag(self.TAG_IMPUT,self.findByTag(self.TAG_FORM,self.findByTag(self.TAG_HEADER,driver)))
        inputElement = self.typeIn(self.textSearch,inputElement)

    def getSongSet(self,performerPage):
        songLineList = self.findAllByClass(CifrasClubWebScraper.CLASS_ARTIST_LINK,performerPage)
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
