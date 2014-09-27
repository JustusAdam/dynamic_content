from framework.url_tools import Url

__author__ = 'justusadam'

import unittest


class MyTestCase(unittest.TestCase):
 def testUrl(self):
  url = '/something/all/my/#locationlocationloaction?get=3?fun=all'
  testElement = Url(url)

  self.assertEqual(testElement.path[:], ['something', 'all', 'my'])
  self.assertEqual(testElement.path.trailing_slash, True)
  self.assertEqual(testElement.path.starting_slash, True)
  self.assertEqual(str(testElement.path), '/something/all/my/')
  self.assertEqual(testElement.path[0], 'something')

  self.assertEqual(str(testElement.location), '#locationlocationloaction')
  self.assertEqual(testElement.location.location, 'locationlocationloaction')

  self.assertEqual(testElement.get_query['get'], '3')
  self.assertEqual(testElement.get_query['fun'], 'all')

  testElement.path = 'something/all/my'

  self.assertEqual(testElement.path[:], ['something', 'all', 'my'])
  self.assertEqual(testElement.path.trailing_slash, False)
  self.assertEqual(testElement.path.starting_slash, False)
  self.assertEqual(str(testElement.path), 'something/all/my')


 def test_something(self):
  self.assertEqual(True, False)


if __name__ == '__main__':
 unittest.main()
