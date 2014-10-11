from django.test import TestCase

from .views import Mashup, HTMLView, ViewView, URLView, TOKEN_LENGTH


class DummyGetRequest():
    method = "get"


class MyMashup(Mashup):
    views = [HTMLView("<p>This is a bunch of html<p>", container="<div class='first-mash'>" + HTMLView.CONTENT_SUB_STRING + "</div>"),
             HTMLView("<p>This is another bunch of html</p>", container="<div class='second-mash'>" + HTMLView.CONTENT_SUB_STRING + "</div>"),
             ]


class MySecondMashup(Mashup):
    views = [ViewView(MyMashup, container="<div class='big-mash-container'>" + ViewView.CONTENT_SUB_STRING + "</div>"),
             HTMLView("<p>A third bunch of HTML</p>"),
             ]


class MyThirdMashup(Mashup):

    views = [URLView("/testing/url", container="<div class='big-mash-container'>" + URLView.CONTENT_SUB_STRING + "</div>"),
             URLView("/test/url"),
             ]


class MashupViewTests(TestCase):

    def test_html_view_mashing(self):

        # Assert that MyMashup gives the expected response
        self.assertEqual(MyMashup.as_view()(DummyGetRequest()).content,
                         b"<div class='first-mash'><p>This is a bunch of html<p></div><div class='second-mash'><p>This is another bunch of html</p></div>")

    def test_view_view_mashing(self):
        # This test might fail because of a failure in HTMLView
        # If both this test and test_html_view_mashing fails, address test_html_view_mashing first

        # Assert that MySecondMashup gives the expected response.
        self.assertEqual(MySecondMashup.as_view()(DummyGetRequest()).content,
                         b"<div class='big-mash-container'><div class='first-mash'><p>This is a bunch of html<p></div><div class='second-mash'><p>This is another bunch of html</p></div></div><p>A third bunch of HTML</p>")

    def test_url_view(self):
        # Tough to test URL view.
        # For now, we'll assert that we got something of the right length out of it.
        dummy_token = ''.join(" " for _ in range(TOKEN_LENGTH))

        target_length = 0
        for view in MyThirdMashup.views:
            expected_content = view.jquery_detector % (view.jquery_loader, view.javascript_loader)
            expected_content = expected_content.replace(URLView.TOKEN_SUB_STRING, dummy_token)
            expected_content = expected_content .replace(URLView.URL_SUB_STRING, view.content)

            target_length += len(expected_content)

            if hasattr(view, "container") and view.container:
                target_length += len(view.container.replace(view.CONTENT_SUB_STRING, ""))

        # Assert that the response has the correct length
        self.assertEqual(len(MyThirdMashup.as_view()(DummyGetRequest()).content), target_length)


class MashupComponentInitTests(TestCase):

    def test_container_subclassing(self):

        class MyHTMLView(HTMLView):
            container = "test_container"

        htmlview = HTMLView("some content")
        myhtmlview = MyHTMLView("some content")
        mysecondhtmlview = MyHTMLView("some content", container="test_container_2")

        # Assert that the instance of HTMLView has no container
        self.assertTrue((not hasattr(htmlview, "container")) or (not htmlview.container))
        # Assert that the first instance of MyHTMLView has the container we gave it.
        self.assertEqual(myhtmlview.container, "test_container")
        # Assert that the second instance of MyHTMLView has the container we gave it.
        self.assertEqual(mysecondhtmlview.container, "test_container_2")
