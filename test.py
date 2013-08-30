#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import *
from domain_controller.domain import Domain
from sql_controller import Base
from settings import conf


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
    time = Column(String(123))
    message = Column(String(200))
    domain_uuid = Column(String(100), ForeignKey('domains.uuid'))

    def __init__(self, message, domain_uuid):
        self.message = message
        self.domain_uuid = domain_uuid
        self.time = "asdasd"

    def __repr__(self):
        return "<Action('%s', '%s', '%s')>" % (
            self.time, self.message, self.domain_uuid)


class Controller(object):
    table_names = {"domains": Domain}

    def __init__(self):
        self.connection = conf.SQL["connection"]
        self.engine = create_engine(self.connection)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def add_domain(self, dom):
        self.session.add(dom)
        self.session.commit()

ctrl = Controller()
#ctrl.add_domain(Host("localhost"))
#ctrl.add_domain(Domain("asd", 15642))
ctrl.add_domain(Action("test start!!!!", "d280985e-118d-11e3-a4e9-60a44ca92ac2"))

