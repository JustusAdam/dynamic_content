import unittest
from dycc.util import clean

__author__ = 'Justus Adam'
__version__ = '0.1'


s1 = """
<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title></title>
    <script src="some" />
    <script src="kkkkwever"></script>
    <script />
    </script>
</head>
<body>
<h1>Some Title
</h1>
<iframe src="bollocks">
MyFramecontens
</iframe>

</body>
</html>
"""

s2 = """

"""


class TestCleanInput(unittest.TestCase):
    def test_severity_1(self):
        text = clean.remove_dangerous_tags(s1, 0)
        self.assertNotIn('<script src="some" />', text)
        self.assertNotIn('<script src="kkkkwever"></script>', text)
        self.assertNotIn('<script />\n    </script>', text)
        self.assertNotIn('</script>', text)
        self.assertNotIn('<iframe src="bollocks">\nMyFramecontens\n</iframe>', text)
        text2 = clean.remove_dangerous_tags(s1, 1)
        self.assertNotIn('<script src="some" />', text2)
        self.assertNotIn('<script src="kkkkwever"></script>', text2)
        self.assertNotIn('<h1>Some Title\n</h1>', text2)
        self.assertNotIn('<body>', text2)
        self.assertNotIn('<html>', text2)
        self.assertNotIn('</html>', text2)
