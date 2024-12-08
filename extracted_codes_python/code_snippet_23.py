#!/usr/bin/python3
"""This module defines a base class for all models in our app"""
import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DATETIME
from sqlalchemy.orm import sessionmaker
from models import storage_type

# create a session and bind it to the base in sqlalchemy

Base = declarative_base()


class BaseModel(Base):
    """A base class for all models

    Attributes:
    id (sqlalchemy String): The BaseModel id
    created_at (sqlalchemy DateTime): The datetime at creation
    updated_at (sqlalchemy DateTime): The datetime of last update
    """
    __tablename__='findme'
    
    id = Column(String(60),
                nullable=False,
                primary_key=True,
                unique=True)
    created_at = Column(DATETIME,
                        nullable=False,
                        default=datetime.utcnow())
    updated_at = Column(DATETIME,
                        nullable=False,
                        default=datetime.utcnow())

    def __init__(self, *args, **kwargs):
        """Instatntiates a new model"""
        if not kwargs:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
        else:
            if 'id' in kwargs and kwargs['id'] is not None:
                self.id = kwargs['id']
            else:
                self.id = str(uuid.uuid4())

            if 'created_at' in kwargs and kwargs['created_at'] is not None:
                self.created_at = datetime.fromisoformat(kwargs['created_at'])
            else:
                self.created_at = datetime.now()

            if 'updated_at' in kwargs and kwargs['updated_at'] is not None:
                self.updated_at = datetime.fromisoformat(kwargs['updated_at'])
            else:
                self.updated_at = datetime.now()

            if storage_type == 'db':
                if not hasattr(kwargs, 'id'):
                    setattr(self, 'id', str(uuid.uuid4()))
                if not hasattr(kwargs, 'created_at'):
                    setattr(self, 'created_at', datetime.now())
                if not hasattr(kwargs, 'updated_at'):
                    setattr(self, 'updated_at', datetime.now())

            """for t in kwargs:
                if t in ['created_at', 'updated_at']:
                    setattr(self, t, datetime.fromisoformat(kwargs[t]))
                elif t != '__class__':
                    setattr(self, t, kwargs[t])
            if storage_type == 'db':
                if not hasattr(kwargs, 'id'):
                    setattr(self, 'id', str(uuid.uuid4()))
                if not hasattr(kwargs, 'created_at'):
                    setattr(self, 'created_at', datetime.now())
                if not hasattr(kwargs, 'updated_at'):
                    setattr(self, 'updated_at', datetime.now())"""

    def __str__(self):
        """Returns a string representation of the instance"""
        return '[{}] ({}) {}'.format(
                self.__class__.__name__, self.id, self.__dict__)

    def save(self):
        """Updates updated_at with current time when instance is changed"""
        from models import storage
        self.updated_at = datetime.now()
        storage.new(self)
        storage.save()

    def reload(self):
        """Reloads the database"""
        from models import storage
        storage.reload()
    
    def to_dict(self):
        """Convert instance into dict format"""
        dictionary = self.__dict__.copy()
        class_name = self.__class__.__name__
        print(f"Class name: {class_name}")
        dictionary['__class__'] = class_name
        for t in dictionary:
            if isinstance(dictionary[t], datetime):
                dictionary[t] = dictionary[t].isoformat()
        if '_sa_instance_state' in dictionary.keys():
            del(dictionary['_sa_instance_state'])
        return dictionary

    def delete(self):
        '''the current instance is deleted from storage'''
        from models import storage
        storage.delete(self)
