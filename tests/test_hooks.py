from framework import hooks

__author__ = 'justusadam'
__version__ = '0.1'

import unittest


class MyTestCase(unittest.TestCase):
    def setUp(self):

        @hooks.register(8)
        class TestHook1(hooks.ClassHook):
            hook_name = 'testhook1'

            def __init__(self, arg=0):
                super().__init__()
                self.arg = arg

            def __call__(self, *args, **kwargs):
                return self.arg, args, kwargs

            def method(self, g):
                return self.arg, g

            def method2(self):
                if not self.arg == 0:
                    return self.arg

        TestHook1.register_class()

        TestHook1.register_instance(TestHook1(3))

        TestHook1(6).register_instance()

        self.TestHook1 = TestHook1

    def test_all_called(self):

        res1 = tuple(self.TestHook1.yield_call_hooks(2,3, l=6))

        for a in (
            (0, (2, 3), {'l':6}),
            (8, (2, 3), {'l':6}),
            (3, (2, 3), {'l':6}),
            (6, (2, 3), {'l':6})
        ):

            self.assertIn(a, res1)

        res2 = tuple(
            self.TestHook1.yield_call_hooks_with(
                lambda self, g: self.method(g),
                4
            )
        )

        for a in (
            (0, 4),
            (8, 4),
            (3, 4),
            (6, 4)
        ):
            self.assertIn(a, res2)

        res3 = self.TestHook1.return_call_hooks_with(
            lambda self: self.method2()
        )

        self.assertIn(
            res3,
            (8, 3, 6)
        )


if __name__ == '__main__':
    unittest.main()
