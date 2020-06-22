from SqlAlchemyHelper import *

CLASS_ORIGINAL_CONTENT = 'OriginalContent'

ORIGINAL_CONTENT = CLASS_ORIGINAL_CONTENT.lower()

Model = getNewModel()

def getManyToMany(son, father):
    return Table(f'{son}_to_{father}', Model.metadata,
        Column(f'{son}_id', Integer, ForeignKey(f'{son}.id')),
        Column(f'{father}_id', Integer, ForeignKey(f'{father}.id')))
