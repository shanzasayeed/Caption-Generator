from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column,Integer,String,DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import sessionmaker
Base=declarative_base()
class User(Base):

    __tablename__='users'
    id=Column(Integer,primary_key=True)
    username=Column(String(50),nullable=False)
    email=Column(String(50),unique=True)
    password=Column(String(64))
    created_at=Column(DateTime, default=datetime.now)

    def __str__(self):
        return self.username

class Upload(Base):
    __tablename__='uploads'
    id=Column(Integer,primary_key=True)
    title=Column(String(50),nullable=False)
    description=Column(String(100))
    file_path=Column(String(100))
    created_at=Column(DateTime, default=datetime.now)
    user_id= Column(Integer, ForeignKey('users.id'))

    def __str__(self):
        return self.title
    

class ChatMessage(Base):
    __tablename__='chat_messages'
    id=Column(Integer,primary_key=True)
    message=Column(String(100))
    response=Column(String(100))
    upload = Column(Integer, ForeignKey('uploads.id'))
    created_at=Column(DateTime, default=datetime.now)
    user_id= Column(Integer, ForeignKey('users.id'))
    
    def __str__(self):
        return self.message
    

def open_db():
    engine=create_engine('sqlite:///project.db',echo=True)    
    session=sessionmaker(bind =engine)
    return session()
def add_to_db(object):
    db=open_db()
    db.add(object)
    db.commit()
    db.close()

if __name__== '__main__':
    engine=create_engine('sqlite:///project.db',echo=True)
    Base.metadata.create_all(engine)


  
