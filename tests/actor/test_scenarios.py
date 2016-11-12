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



if __name__ == '__main__':
    unittest.main()
