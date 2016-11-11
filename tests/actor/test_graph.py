import unittest
import actor.actor as act
import actor.graph as g


class GraphTestCase(unittest.TestCase):

    def test_graph(self):
        graph = act.ActorSystem("graph")

        node1 = graph.actor_of(g.BasicNode, name="node1")
        node2 = graph.actor_of(g.BasicNode, name="node2")
        node3 = graph.actor_of(g.BasicNode, name="node3")

        edge1 = graph.actor_of(g.Edge, name="n1n2", node1=node1, node2=node2)
        edge2 = graph.actor_of(g.Edge, name="n1n3", node1=node1, node2=node3)

        node1.tell(g.Message.create('add_edge', edge1))
        node2.tell(g.Message.create('add_edge', edge1))

        node1.tell(g.Message.create('add_edge', edge2))
        node3.tell(g.Message.create('add_edge', edge2))

        node1.tell(g.Message.create('broadcast', 'around the world'))

        node1.tell(g.Message.create('remove_edge', edge2))
        node3.tell(g.Message.create('remove_edge', edge2))

        node1.tell(g.Message.create('broadcast', 'second time'))

    def test_graph_utilities(self):
        graph = act.ActorSystem("graph")

        node1 = graph.actor_of(g.BasicNode, name="node1")
        node2 = graph.actor_of(g.BasicNode, name="node2")
        node3 = graph.actor_of(g.BasicNode, name="node3")

        # edge1 = graph.actor_of(g.Edge, name="n1n2", node1=node1, node2=node2)
        # edge2 = graph.actor_of(g.Edge, name="n1n3", node1=node1, node2=node3)

        g.Utility.insert_edge(graph, node1, node2, name="n1n2")
        g.Utility.insert_edge(graph, node1, node3, name="n1n3")

        node1.tell(g.Message.create('broadcast', 'around the world'))
        #
        # node1.tell(g.Message.create('remove_edge', edge2))
        # node3.tell(g.Message.create('remove_edge', edge2))

        node1.tell(g.Message.create('broadcast', 'second time'))

    def test_edge_insert_graph(self):
        graph = act.ActorSystem("graph")

        node1 = graph.actor_of(g.BasicNode, name="node1")
        node2 = graph.actor_of(g.BasicNode, name="node2")
        node3 = graph.actor_of(g.BasicNode, name="node3")

        edge1 = graph.actor_of(g.Edge, name="n1n2", node1=node1, node2=node2)
        edge2 = graph.actor_of(g.Edge, name="n1n3", node1=node1, node2=node3)

        edge1.tell(g.Message.create('edge_insert', None))
        edge2.tell(g.Message.create('edge_insert', None))

        node1.tell(g.Message.create('broadcast', 'around the world'))

        edge2.tell(g.Message.create('edge_remove', None))

        node1.tell(g.Message.create('broadcast', 'second time'))

if __name__ == '__main__':
    unittest.main()
