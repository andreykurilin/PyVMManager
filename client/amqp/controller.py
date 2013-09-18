#!/usr/bin/env python
import uuid
import pika
from prettytable import PrettyTable
from server.amqp.controller import amqp_init
from server.utils.settings import conf

__author__ = 'akurilin'


class Controller(object):
    def __init__(self, host):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host))
        self.channel = self.connection.channel()
        amqp_init(channel=self.channel)
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, data):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        if data["handler"] == "networking":
            rkey = "network"
        else:
            rkey = "manage"
        self.channel.basic_publish(exchange=conf.AMQP["exchange"],
                                   routing_key=rkey,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,),
                                   body=str(data))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def print_info(self, info):
        if "name" not in info:
            print info
        else:
            info = eval(info)
            info_table = PrettyTable(["Name", "UUID", "State", "Memory", "VCPU"])
            info_table.padding_width = 1
            info_table.add_row([info["name"], info["uuid"], info["state"],
                                info["memory"], info["vcpu"]])
            print info_table

    def print_list(self, info):
        info = eval(info)

        list_table = PrettyTable(["id", "Name", "Status"])
        list_table.align["Name"] = "l"
        list_table.padding_width = 1
        for dom in info.values():
            list_table.add_row([dom["id"], dom["name"], dom["status"]])
        print list_table

