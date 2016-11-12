import abc
import actor as act
from actor import Message


class Node(act.ProtocolActor):
    __metaclass__ = abc.ABCMeta

    def __init__(self, context, name=None, ):
        super(Node, self).__init__(context, name)
        self.edge_nodes = set()

    def add_edge(self, node):
        self.log.debug("Adding Edge")
        self.edge_nodes.add(node)
        self.log.debug("Edges: {}".format(self.edge_nodes))

    def remove_edge(self, node):
        self.log.debug("Removing Edge from: {}".format(self.edge_nodes))
        self.edge_nodes.remove(node)
        self.log.debug("Edges: {}".format(self.edge_nodes))

    def on_add_edge(self, msg, sender):
        self.add_edge(msg['data'])

    def on_remove_edge(self, msg, sender):
        self.remove_edge(msg['data'])

    def is_from_edge(self, sender):
        return sender in self.edge_nodes


class Edge(act.ProtocolActor):
    def __init__(self, context, node1, node2, name=None):
        super(Edge, self).__init__(context, name)
        self.node1 = node1
        self.node2 = node2

    def on_edge_insert(self, msg, sender):
        self.node1.tell(Message.create('add_edge', self.get_ref()), self.get_ref())
        self.node2.tell(Message.create('add_edge', self.get_ref()), self.get_ref())

    def on_edge_remove(self, msg, sender):
        self.node1.tell(Message.create('remove_edge', self.get_ref()), self.get_ref())
        self.node2.tell(Message.create('remove_edge', self.get_ref()), self.get_ref())

    def on_default(self, msg, sender):
        self.log.debug("Edge Got Msg: {}, {}".format(msg, sender))
        self.log.debug("Edge Config: {} - {}".format(self.node1, self.node2))
        if sender == self.node1:
            self.log.debug("Relaying to node2")
            self.node2.tell(msg, sender=self.get_ref())
        elif sender == self.node2:
            self.log.debug("Relaying to node1")
            self.node1.tell(msg, sender=self.get_ref())
        else:
            raise EdgeException("{}: Edge Received Message Not From Endpoint, from: {}".format(self.uuid, sender))


class BasicNode(Node):

    def on_broadcast(self, msg, sender):
        for edge in self.edge_nodes:
            edge.tell(Message.create('datum', msg['data']), sender=self.get_ref())


class Utility(object):
    @staticmethod
    def insert_edge(graph, node1, node2, name=None, edge_type=None, *args, **kwargs):
        edge_type = Edge if edge_type is None else edge_type
        edge = graph.actor_of(edge_type, name=name, node1=node1, node2=node2, *args, **kwargs)
        node1.tell(Message.create('add_edge', edge))
        node2.tell(Message.create('add_edge', edge))

    @staticmethod
    def remove_edge(edge):
        edge.node1.tell(g.Message.create('remove_edge', edge))
        edge.node2.tell(g.Message.create('remove_edge', edge))


class EdgeException(Exception):
    pass


class NodeException(Exception):
    pass

