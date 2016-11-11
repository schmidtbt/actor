import unittest
import actor.actor as act


class ActorTest(unittest.TestCase):

    def test_actor(self):
        sys = act.ActorSystem("my_sys")
        ref1 = sys.actor_of(act.SimpleActor, name='ref1')
        ref2 = sys.actor_of(act.Ping, other=ref1, name='ref2')

        ref1.tell("msg")
        ref2.tell("diff msg")

        sys.context.send(ref1, 'from the outside')

    def test_actor_collision(self):
        sys = act.ActorSystem("my_sys")
        ref1 = sys.actor_of(act.SimpleActor, name='ref1')
        self.assertRaises(act.ContextException, sys.actor_of, act.Ping, other=ref1, name='ref1')


if __name__ == '__main__':
    unittest.main()
