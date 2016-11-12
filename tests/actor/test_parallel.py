import unittest
import time
import actor.actor as act
import actor.parallel as para


class ActorTest(unittest.TestCase):

    def test_actor(self):
        sys = act.ActorSystem("my_sys", context=para.ThreadingContext(dispatcher=para.UniqueThreader))
        ref1 = sys.actor_of(act.SimpleActor, name='ref1')
        ref2 = sys.actor_of(act.SimpleActor, name='ref2')

        time.sleep(1)

        ref1.tell("msg")
        ref2.tell("diff msg")

        sys.context.send(ref1, 'from the outside')

        time.sleep(4)


if __name__ == '__main__':
    unittest.main()
