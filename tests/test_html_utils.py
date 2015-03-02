import unittest
from framework.util import html
from framework.util.html import transform



class TestElementsRendering(unittest.TestCase):
    def test_a(self):
        href = 'http://github.com'
        text = 'Github'

        element = html.A(text, href=href)

        self.assertEqual(
            str(element),
            '<a href="{href}">{text}</a>'.format(href=href, text=text)
        )

    def test_list_plain(self):
        elements = ('hallo', '123', 'content')

        list_ = html.Li(*elements)

        self.assertEqual(
            str(list_),
            '<ul>{}</ul>'.format(
                ''.join('<li>{}</li>'.format(a) for a in elements)
            )
        )


    def test_list_with_id_and_classes(self):
        elements = ('hallo', '123', 'content')
        classes = ('somecool', 'l9ui', 'kksd')

        id_ = 'someid'

        list_ = html.Li(*elements, element_id=id_, classes=classes)

        rendered_classes = 'class="somecool l9ui kksd"'
        rendered_id = 'id="someid"'

        heads = tuple(
            string.format(id=rendered_id, classes=rendered_classes)
            for string in ('<ul {id} {classes}>', '<ul {classes} {id}>')
        )

        content = ''.join('<li>{}</li>'.format(c) for c in elements)

        self.assertIn(
            str(list_),
            tuple(
                '{}{}</ul>'.format(head, content) for head in heads
            )
        )

    def test_lsit_with_a_as_content(self):
        elements = (
            html.A('Github', href='https://github.com'),
            html.A('Travis', href='//travis-ci.org')
        )

        l = html.List(
            *elements,
            classes='awesome'
        )

        self.assertEqual(
            str(l),
            '<ul class="awesome">{}</ul>'.format(
                ''.join('<li>{}</li>'.format(e) for e in elements)
            )
        )


class TestTransform(unittest.TestCase):
    def test_to_html_head(self):
        for elements, result in (
            ((), ''),
            (('hello', [], {}), 'hello')
        ):
            rendered = transform.to_html_head(*elements)

            self.assertEqual(rendered, result)
