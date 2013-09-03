#!/usr/bin/env python

from sqlalchemy import *

from sqlalchemy.orm import *
from sql_controller.tables import *
from settings import conf
from domain_controller.domain import Domain

__author__ = 'akurilin'


class Controller(object):
    states_list = []

    def __init__(self):
        self.connection = conf.SQL["connection"]
        self.engine = create_engine(self.connection)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        Controller.states_list = []
        for n in range(0, 9):
            state_info = conf.State[str(n)].split(";")
            Controller.states_list.append(
                State(n + 1, state_info[0], state_info[1]))
        self.test_state_table()

    def add_record(self, record):
        self.session.add(record)
        self.session.commit()

    def test_domain_table(self, domains_list):
        bd_domains = {}
        for domain in self.session.query(Domain):
            bd_domains[domain.uuid_str] = domain
        for domain in domains_list:
            if domain.UUIDString() not in bd_domains.keys():
                dom_info = domain.info()
                dom = Domain(domain.name(), dom_info[1], vcpu=dom_info[3],
                             uuid_str=domain.UUIDString(), state=dom_info[0])
                self.add_record(dom)
                self.add_record(Action("Added to BD.", dom.uuid_str))
            elif domain.info()[0] != bd_domains[domain.UUIDString()].state_id:
                self.session.query(Domain).\
                    filter(Domain.uuid_str == domain.UUIDString()).\
                    update({"state_id": domain.info()[0]})
                self.session.commit()
                self.add_record(Action("Daemon: state is changed.",
                                       domain.UUIDString()))

    def test_state_table(self):
        bd_states = {}
        for state in self.session.query(State):
            bd_states[state.id] = state
        for state in Controller.states_list:
            if state.id not in bd_states.keys():
                self.add_record(state)
            else:
                if state.description != bd_states[state.id].description \
                        or state.name != bd_states[state.id].name:
                    self.session.query(State).filter(State.id == state.id).\
                        update({"name": state.name,
                                "description": state.description})
                    self.session.commit()