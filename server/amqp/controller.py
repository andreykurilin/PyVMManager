#!/usr/bin/env python
import pika
from server.utils.settings import conf
from server.domain_controller.controller import AlreadyCreatedVMError, \
    NotCreatedVMError, ConnectionError, NotRunningError

__author__ = 'akurilin'


def amqp_init(channel=None, host=conf.AMQP["host"],
              exchange=conf.AMQP["exchange"]):
    if channel is None:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host))
        channel = connection.channel()
    channel.exchange_declare(exchange=exchange, type='direct')
    channel.queue_declare(queue='log')
    for queue_name in ("manage", "network"):
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(exchange=exchange, queue=queue_name,
                           routing_key=queue_name)
        channel.queue_bind(exchange=exchange, queue="log",
                           routing_key=queue_name)


class Controller(object):
    def __init__(self, queue, respond=False, no_ack=False):
        self.queue = queue
        self.respond = respond
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=conf.AMQP["host"]))
        self.channel = self.connection.channel()
        amqp_init(self.channel)
        self.channel.basic_qos(prefetch_count=1)
        if no_ack:
            self.channel.basic_consume(self.on_request, queue=self.queue,
                                       no_ack=True)
        else:
            self.channel.basic_consume(self.on_request, queue=self.queue)

    def on_request(self, ch, method, props, body):
        self.result = None
        data = eval(body)
        if "uri" not in data:
            data["uri"] = conf.General["uri"]
        func = self.__getattr__(data["handler"])
        self.result = func(data)
        print " [.] {0} - {1}: {2}".format(self.queue, data["handler"],
                                           self.result)

        if self.respond:
            ch.basic_publish(exchange="",
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(
                                 correlation_id=props.correlation_id),
                             body=str(self.result))
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.start_consuming()