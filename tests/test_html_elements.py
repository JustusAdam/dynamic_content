import unittest
from framework.util import html



class TestRendering(unittest.TestCase):
    def test_a(self):
        href = 'http://github.com'
        text = 'Github'

        element = html.A(text, href=href)

        self.assertEqual(
            str(element),
            '<a href="{href}">{text}</a>'.format(href=href, text=text)
        )

    def test_list(self):
        elements = ('hallo', '123', 'content')

        list_ = html.Li(*elements)

        self.assertEqual(
            str(list_),
            '<ul>{}</ul>'.format(
                ''.join('<li>{}</li>'.format(a) for a in elements)
            )
        )


        classes = ('somecool', 'l9ui', 'kksd')

        id_ = 'someid'

        list_ = html.Li(*elements, element_id=id_, classes=classes)

        heads = (
            '<ul class="somecool l9ui kksd" id="someid">',
            '<ul id="someid" class="somecool l9ui kksd">'
        )

        content = ''.join('<li>{}</li>'.format(content) for content in elements)

        self.assertIn(
            str(list_),
            (
                '{}{}</ul>'.format(head, content) for head in heads
            )
        )
