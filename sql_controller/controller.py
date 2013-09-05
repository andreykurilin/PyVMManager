#!/usr/bin/env python

from sqlalchemy import *

from sqlalchemy.orm import *
from sql_controller.tables import *
from utils.settings import conf
from domain_controller.domain import Domain
from domain_controller.controller import Controller as DOMController

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
        self.test_state_tables()

    def add_record(self, record):
        self.session.add(record)
        self.session.commit()

    def get_hosts(self):
        hosts = []
        for host in self.session.query(Host):
            hosts.append(host)
        return hosts

    def check_domain_table(self, domains_list, host_id=1):
        dom_bd = {}
        for dom in self.session.query(Domain):
            dom_bd[dom.uuid_str] = dom
        for dom in domains_list:
            if dom.UUIDString() not in dom_bd.keys():
                domain = Domain(dom.name(), dom.info()[1], vcpu=dom.info()[3],
                                uuid_str=dom.UUIDString(),
                                state=dom.info()[0], host_id=host_id)
                self.add_record(domain)
                self.add_record(Action("Added to db.", domain.uuid_str))
            elif dom.info()[0] != dom_bd[dom.UUIDString()].state_id:
                action = Action("State is changed from {0} to {1}".
                                format(dom_bd[dom.UUIDString()].state_id,
                                       dom.info()[0]), dom.UUIDString())
                self.add_record(action)
                self.session.query(Domain).\
                    filter(Domain.uuid_str == dom.UUIDString()).\
                    update({"state_id": dom.info()[0]})
                self.session.commit()

    def check_domain_tables(self):
        bd_domains = {}
        for dom in self.session.query(Domain):
            bd_domains[dom.uuid_str] = dom
        for host in self.get_hosts():
            ctrl = DOMController(host.name)
            self.check_domain_table(ctrl.get_domains_list(), host.id)

    def test_state_tables(self):
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