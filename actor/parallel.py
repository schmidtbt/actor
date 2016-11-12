import threading
import Queue
from actor import Context, ContextException, ActorRef, Actor
from log import get_logger


class ThreadingContext(Context):
    """
    Context threads the individual actors (as opposed to recursion)
    """
    def __init__(self, dispatcher=None):
        Context.__init__(self)
        self.queue = Queue.Queue()
        self.dispatcher = dispatcher if dispatcher is not None else SingleThreader

    def start(self):
        self.log.info("Creating dispatcher = {}".format(self.dispatcher))
        harness = self.dispatcher(self.queue, self)
        harness.start()

    def shutdown(self):
        pass

    def launch_actor(self, actor_type, *args, **kwargs):
        tqueue = Queue.Queue()
        self.queue.put(('add', actor_type, args, kwargs, tqueue))
        waiting = True
        while waiting:
            new_id = tqueue.get()
            ref = ActorRef(new_id, self)
            tqueue.task_done()
            waiting = False
        return ref

    def send(self, to, msg, sender=None):
        self.queue.put(('msg', to, msg, sender))


class SingleThreader(threading.Thread):
    """
    Everything executes in a single context
    """

    def __init__(self, queue, context):
        threading.Thread.__init__(self)
        self.queue = queue
        self.log = get_logger(self.__class__.__name__)
        self.context = context
        self.actors = {}
        self.daemon = True

    def add_actor(self, actor):
        if actor.uuid in self.actors:
            raise ContextException("Name collision while adding actor")
        self.actors[actor.uuid] = actor

    def get_actor_ref_by_id(self, unique_id):
        return ActorRef(unique_id, self)

    def get_actor_by_ref(self, ref):
        return self.actors[ref.uuid]

    def handle_add_actor(self, obj):
        self.log.debug("Adding Actor: {}".format(obj))
        actor_type = obj[1]
        args = obj[2]
        kwargs = obj[3]
        reply_queue = obj[4]
        real_actor = actor_type(self.context, *args, **kwargs)
        self.add_actor(real_actor)
        reply_queue.put(real_actor.uuid)
        self.log.debug("Actors: {}".format(self.actors))

    def handle_msg(self, obj):
        to = obj[1]
        msg = obj[2]
        sender = obj[3]
        self.log.debug("Preparing Message: To: {} - From: {} - Msg: {}".format(to, sender, msg))
        if isinstance(to, ActorRef):
            to = self.get_actor_by_ref(to)
        if isinstance(sender, Actor):
            sender = self.get_actor_ref_by_id(sender)
        self.log.debug("Sending Message: To: {} - From: {} - Msg: {}".format(to, sender, msg))
        to.receive(msg, sender)

    def run(self):
        self.log.debug("Initializing: {}".format(threading.current_thread()))
        while True:
            try:
                obj = self.queue.get()
                self.log.info("Got new msg: {}".format(obj))
                if len(obj) > 1:
                    if obj[0] == 'add':
                        self.handle_add_actor(obj)
                    if obj[0] == 'msg':
                        self.handle_msg(obj)
            except Exception, err:
                self.log.error("An Error Occurred While Processing Message")
                print(err)


class UniqueThreader(SingleThreader):
    """
    One unique thread per actor
    """
    def __init__(self, queue, context):
        SingleThreader.__init__(self, queue, context)
        self.actor_queues = {}

    def add_actor(self, actor, queue=None):
        if actor.uuid in self.actors:
            raise ContextException("Name collision while adding actor")
        self.actors[actor.uuid] = actor
        self.actor_queues[actor.uuid] = queue

    def handle_add_actor(self, obj):
        self.log.debug("Adding Actor: {}".format(obj))
        actor_type = obj[1]
        args = obj[2]
        kwargs = obj[3]
        reply_queue = obj[4]
        real_actor = actor_type(self.context, *args, **kwargs)
        harness = self.ThreadedActorHarness(real_actor)
        harness.start()
        self.add_actor(real_actor, queue=harness.queue)
        reply_queue.put(real_actor.uuid)
        self.log.debug("Actors: {}".format(self.actors))

    def handle_msg(self, obj):
        to = obj[1]
        msg = obj[2]
        sender = obj[3]
        self.log.debug("Preparing Message: To: {} - From: {} - Msg: {}".format(to, sender, msg))
        if isinstance(to, Actor):
            to = self.get_actor_ref_by_id(to)
        if isinstance(sender, Actor):
            sender = self.get_actor_ref_by_id(sender)
        self.log.debug("Sending Message: To: {} - From: {} - Msg: {}".format(to, sender, msg))
        self.actor_queues[to.uuid].put((msg, sender))

    class ThreadedActorHarness(threading.Thread):

        def __init__(self, actor):
            threading.Thread.__init__(self)
            self.actor = actor
            self.log = get_logger("ThreadedActorHarness")
            self.queue = Queue.Queue()
            self.daemon = True

        def run(self):
            self.log.debug("Starting Harness Execution - {}".format(self.actor.uuid))
            while True:
                msg = self.queue.get()
                self.log.debug("RECV: {}".format(msg))
                self.actor.receive(msg[0], msg[1])


class Mailbox(object):

    def __init__(self):
        self.mailbox = Queue.Queue()













