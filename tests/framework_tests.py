__author__ = 'justusadam'

import unittest


class MyTestCase(unittest.TestCase):
 def testPage(self):
  from framework.page import Component

  testComponentA = Component('Component A', 'Content A', {'style a', 'more style a'})
  testComponentB = Component('Component B', 'Content B', {'style b', 'more style b'})

  result = Component('Component A', 'Content AContentB', {'style a', 'more style a', 'style b', 'more style b'})

  combined = testComponentA + testComponentB

  for component in combined, result:
   print(component.metatags)
   print(component.stylesheets)
   print(component.content)
   print(component.scripts)
   print(component.title)


if __name__ == '__main__':
 unittest.main()
