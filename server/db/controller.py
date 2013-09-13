#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import *
from server.domain_controller.domain import Domain
from server.domain_controller.controller import Controller as DOMController

from server.db.tables import *
from server.utils.settings import conf
from server.utils.xml_shaper import *

__author__ = 'akurilin'


class Controller(object):
    states_list = []

    def __init__(self):
        self.connection = conf.SQL["connection"]
        self.engine = create_engine(self.connection)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def add_record(self, record):
        self.session.add(record)
        self.session.commit()

    def get_hosts(self):
        hosts = []
        for host in self.session.query(Host):
            hosts.append(host)
        return hosts

    def get_domains(self):
        bd_domains = {}
        for dom in self.session.query(Domain):
            bd_domains[dom.uuid_str] = dom
        return bd_domains

    def get_addresses(self):
        bd_addresses = {}
        for ip_address in self.session.query(IPAddr):
            bd_addresses[ip_address.ip] = ip_address.domain_mac
        return bd_addresses

    def check_domain_table(self, domains_list, host_id=1):
        dom_db = self.get_domains()
        for dom in domains_list:
            if dom.UUIDString() not in dom_db.keys():
                macs = xml_parser(dom.XMLDesc(0), "devices/interface/mac",
                                  "address")

                for mac_address in macs:
                    mac = mac_address
                domain = Domain(dom.name(), dom.info()[1], vcpu=dom.info()[3],
                                uuid_str=dom.UUIDString(), mac_address=mac,
                                state=dom.info()[0], host_id=host_id)
                self.add_record(domain)
                self.add_record(Action("Added to db.", domain.uuid_str))
            elif dom.info()[0] != dom_db[dom.UUIDString()].state_id:
                action = Action("State is changed from {0} to {1}".
                                format(dom_db[dom.UUIDString()].state_id,
                                       dom.info()[0]), dom.UUIDString())
                self.add_record(action)
                self.session.query(Domain).\
                    filter(Domain.uuid_str == dom.UUIDString()).\
                    update({"state_id": dom.info()[0]})
                self.session.commit()
        dom_db = self.get_domains()
        for dom_uuid in dom_db.keys():
            if dom_uuid not in [dom.UUIDString() for dom in domains_list]:
                self.add_record(Action("Domain deleted.", dom_uuid))

    def check_domain_tables(self):
        for host in self.get_hosts():
            ctrl = DOMController(host.name)
            self.check_domain_table(ctrl.get_domains_list(), host.id)

    def update_address(self, ip_address, mac_address="-"):
        if mac_address == "-":
            availability = 1
        else:
            availability = 0
        self.session.query(IPAddr).filter(IPAddr.ip == ip_address).\
            update({"domain_mac": mac_address, "availability": availability})
        self.session.commit()

    def check_net_table(self, addresses):
        for address in addresses:
            self.update_address(address["ip"], address["mac"])
        bd_addresses = self.get_addresses()
        domains_mac = [domain.mac for domain in self.get_domains().values()]
        for ip_address in bd_addresses.keys():
            if bd_addresses[ip_address] not in domains_mac:
                self.update_address(ip_address)
