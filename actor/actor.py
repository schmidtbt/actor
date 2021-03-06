import abc
import uuid
from log import get_logger


class ActorSystem(object):
    def __init__(self, sys_name, context=None):
        self.sys_name = sys_name
        self.context = context if context is not None else Context()
        self.context.start()
        self.log = get_logger(sys_name)
        self.log.debug("Initialized ActorSystem: {}".format(sys_name))

    def actor_of(self, actor_type, *args, **kwargs):
        """
        @rtype: ActorRef
        """
        self.log.debug("Generating actor of type: {}".format(actor_type))
        ref = self.context.launch_actor(actor_type, *args, **kwargs)
        return ref

    def shutdown(self):
        self.context.shutdown()


class Context(object):
    def __init__(self):
        self.actors = {}
        self.log = get_logger(self.__class__.__name__)
        self.log.debug("Initialized Context")

    def add_actor(self, actor):
        if actor.uuid in self.actors:
            raise ContextException("Name collision while adding actor")
        self.actors[actor.uuid] = actor

    def get_actor_ref_by_id(self, unique_id):
        return ActorRef(unique_id, self)

    def get_actor_by_ref(self, ref):
        return self.actors[ref.uuid]

    def launch_actor(self, actor_type, *args, **kwargs):
        real_actor = actor_type(self, *args, **kwargs)
        self.add_actor(real_actor)
        return real_actor.get_ref()

    def start(self):
        pass

    def shutdown(self):
        pass

    def send(self, to, msg, sender=None):
        self.log.debug("Sending Message: To: {} - From: {} - Msg: {}".format(to, sender, msg))
        if isinstance(to, ActorRef):
            to = self.get_actor_by_ref(to)
        if isinstance(sender, Actor):
            sender = sender.get_ref()
        to.receive(msg, sender)


class ActorRef(object):
    def __init__(self, uuid, context):
        self.uuid = uuid
        self.context = context
        self.log = get_logger("REF-{}".format(self.uuid))

    @staticmethod
    def reference_of(real_actor, system):
        return ActorRef(real_actor.uuid, system)

    def tell(self, msg, sender=None):
        if isinstance(sender, Actor):
            sender = sender.get_ref()
            self.log.warn("Real Actor object being used incorrectly")
        self.context.send(self, msg, sender=sender)

    def __str__(self):
        return "ActorRef[{}]".format(self.uuid)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __hash__(self):
        return hash(self.uuid)


class Actor(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, context, name=None):
        self.context = context
        self.uuid = uuid.uuid4().__str__() if name is None else name
        self.log = get_logger(name)
        self.ref = ActorRef(self.uuid, self.context)

    def uuid(self):
        return self.uuid

    @abc.abstractmethod
    def receive(self, msg, sender=None):
        return

    def get_ref(self):
        return self.ref

    def __str__(self):
        return "{}".format(self.uuid)


class ProtocolActor(Actor):
    __metaclass__ = abc.ABCMeta

    def on_default(self, msg, sender):
        self.log.debug("Default Protocol Case")

    def receive(self, msg, sender=None):
        self.log.debug("received: {}".format(msg))
        Message.validate(msg)
        try:
            cmd = msg['cmd']
            func_name = "on_{}".format(cmd)
            func_callable = getattr(self, func_name)
            self.log.debug("receiver calling: {}".format(func_name))
            func_callable(msg, sender)
        except AttributeError, err:
            self.log.error(err)
            self.log.debug("Defaulting on msg: {}".format(msg))
            self.on_default(msg, sender)


class Message(object):
    @staticmethod
    def create(command, data):
        return {'cmd': command, 'data': data}

    @staticmethod
    def validate(msg, do_raise=True):
        if ('cmd' not in msg) | ('data' not in msg):
            if do_raise:
                raise MessageException("ill-formed command")
            else:
                return False
        return True


class MessageException(Exception):
    pass


class SimpleActor(Actor):
    def receive(self, msg, sender=None):
        self.log.info("Got Msg: {}, from: {}, context: {}".format(msg, sender, self.context))


class ContextException(Exception):
    pass


class ActorException(Exception):
    pass
