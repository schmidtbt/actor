import actor as act
import graph as g


class Ping(act.ProtocolActor):
    def __init__(self, context, other, *args, **kwargs):
        super(Ping, self).__init__(context, *args, **kwargs)
        self.other = other

    def on_ping(self, msg, sender):
        self.log.debug("starting pong")
        self.other.tell(g.Message.create('ping', None))


class Pong(act.ProtocolActor):

    def on_ping(self, msg, sender):
        self.log.debug("Got Ping -- PONG!!")
