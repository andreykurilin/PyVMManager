#!/usr/bin/env python
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

__author__ = 'akurilin'

Base = declarative_base()


class State(Base):
    __tablename__ = 'states'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(200))
    domains = relationship("Domain", backref="state")

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<State('%s','%s','%s', )>" % (
            self.id, self.name, self.description, )


class Host(Base):
    __tablename__ = 'hosts'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    domains = relationship("Domain", backref="host")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Host('%s',)>" % (self.name, )


class Action(Base):
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True)
    time = Column(DateTime, default=func.now())
    message = Column(String(200))
    domain_uuid = Column(String(100), ForeignKey('domains.uuid_str'))

    def __init__(self, message, domain_uuid):
        self.message = message
        self.domain_uuid = domain_uuid

    def __repr__(self):
        return "<Action('%s', '%s', '%s')>" % (
            self.time, self.message, self.domain_uuid)


class IPAddr(Base):
    __tablename__ = 'ip_address'

    ip = Column(String(19), primary_key=True)
    availability = Column(Boolean)
    domain_mac = Column(String(300))

    def __init__(self, ip, domain_mac="-", availability=1):
        self.ip = ip
        self.domain_mac = domain_mac
        self.availability = availability

    def __repr__(self):
        return "<IPAddr('%s', '%s', '%s')>" % (self.ip, self.domain_mac,
                                               self.availability)