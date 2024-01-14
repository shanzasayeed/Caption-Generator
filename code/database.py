from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column,Integer,String,DateTime
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


  
