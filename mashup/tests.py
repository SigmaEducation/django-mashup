from django.test import TestCase

from .views import Mashup, HTMLView, ViewView, URLView, TOKEN_LENGTH


class DummyGetRequest():
    method = "get"


class MyMashup(Mashup):
    views = [HTMLView("<p>This is a bunch of html<p>", container="<div class='first-mash'>{{ mashup }}</div>"),
             HTMLView("<p>This is another bunch of html</p>", container="<div class='second-mash'>{{ mashup }}</div>"),
             ]


class MySecondMashup(Mashup):
    views = [ViewView(MyMashup, container="<div class='big-mash-container'>{{ mashup }}</div>"),
             HTMLView("<p>A third bunch of HTML</p>"),
             ]


class MyThirdMashup(Mashup):

    views = [URLView("/testing/url", container="<div class='big-mash-container'>{{ mashup }}</div>"),
             URLView("/test/url"),
             ]


class MashupViewTests(TestCase):

    def test_html_view_mashing(self):
        self.assertEqual(MyMashup.as_view()(DummyGetRequest()).content,
                         b"<div class='first-mash'><p>This is a bunch of html<p></div><div class='second-mash'><p>This is another bunch of html</p></div>")

    def test_view_view_mashing(self):
        # This test might fail because of a failure in HTMLView
        # If both this test and test_html_view_mashing fails, address test_html_view_mashing first
        self.assertEqual(MySecondMashup.as_view()(DummyGetRequest()).content,
                         b"<div class='big-mash-container'><div class='first-mash'><p>This is a bunch of html<p></div><div class='second-mash'><p>This is another bunch of html</p></div></div><p>A third bunch of HTML</p>")

    def test_url_view(self):
        # Tough to test URL view.
        # For now, we'll assert that we got something of the right length out of it.
        dummy_token = ''.join(" " for _ in range(TOKEN_LENGTH))

        target_length = 0
        for view in MyThirdMashup.views:
            expected_content = view.jquery_detector % (view.jquery_loader, view.javascript_loader)
            expected_content = expected_content.replace("{{ token }}", dummy_token)
            expected_content = expected_content .replace("{{ url }}", view.content)

            target_length += len(expected_content)

            if hasattr(view, "container") and view.container:
                target_length += len(view.container.replace("{{ mashup }}", ""))

        self.assertEqual(len(MyThirdMashup.as_view()(DummyGetRequest()).content), target_length)
