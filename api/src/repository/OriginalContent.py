from SqlAlchemyHelper import Table, Column, Integer, String, ForeignKey, UnicodeText, MetaData

import SqlAlchemyHelper

class OriginalContent(SqlAlchemyHelper.Base):
    __tablename__ = 'original_content'

    id = Column(Integer, primary_key=True)
    performer = Column(String(128))
    name = Column(String(128))
    url = Column(String(1024))
    # visitCount = Column(Integer)
    content = Column(UnicodeText(32768))

    def __init__(self,performer,name,url,content):
        self.performer = performer
        self.name = name
        self.url = url
        self.content = content

    def __repr__(self):
        return f'id = {self.id}\nname = {self.name}\nperformer = {self.performer}\nurl = {self.url}\ncontent = {self.content}'

    # @classmethod
    # def findByName(cls, session, name):
    #     return session.query(cls).filter_by(name=name).all()
