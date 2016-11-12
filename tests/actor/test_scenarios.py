import unittest
import time
import actor.actor as act
import actor.graph as g
import actor.parallel as para
import actor.scenarios as util


class ScenarioTestCase(unittest.TestCase):

    def test_ping_pong(self):
        sys = act.ActorSystem("my_sys", context=para.ThreadingContext(dispatcher=para.UniqueThreader))
        pong = sys.actor_of(util.Pong, name='pong')
        ping = sys.actor_of(util.Ping, other=pong, name='ping')

        ping.tell(g.Message.create('ping', None))

        time.sleep(3)

    def test_pingpong_forever(self):
        graph = act.ActorSystem("graph", context=para.ThreadingContext(dispatcher=para.UniqueThreader))

        node1 = graph.actor_of(util.PingPonger, name="node1")
        node2 = graph.actor_of(util.PingPonger, name="node2")

        edge1 = graph.actor_of(g.Edge, name="n1n2", node1=node1, node2=node2)

        edge1.tell(g.Message.create('edge_insert', None))

        time.sleep(1)

        node1.tell(g.Message.create('ping_pong', 0))

        time.sleep(5)

if __name__ == '__main__':
    unittest.main()
