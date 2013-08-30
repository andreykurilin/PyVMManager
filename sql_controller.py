#!/usr/bin/env python
from sqlalchemy import *
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *
#from domain_controller.domain import Domain

from settings import conf

__author__ = 'akurilin'

Base = declarative_base()


class Controller(object):
    def __init__(self):
        self.connection = conf.SQL["connection"]
        self.engine = create_engine(self.connection)
        self.session = sessionmaker(bind=self.engine)()
#        new_domain = Domain("test_domain", "1482456")
#        self.session.add(new_domain)
#        self.session.


#class Host(Base):
#    __tablename__ = "hosts"
#    id = Column(Integer, primary_key=True)
#    address = Column(String(50))
#    vms = relationship("VM", backref="host")
#
#
#class VM(Base):
#    __tablename__ = "vms"
#
#    id = Column(Integer, primary_key=True)
#    name = Column(String(50))
#    current_state = Column(String(15))
#    parameters = Column(String(100))
#    host_id = Column(Integer, ForeignKey('hosts.id'))
#    actions = relationship("Action", backref="vm")
#
#
#class Action(Base):
#    __tablename__ = "actions"
#
#    id = Column(Integer, primary_key=True)
#    time = Column(String(50))
#    message = Column(String(100))
#    vm_id = Column(Integer)