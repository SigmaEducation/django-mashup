from django.test import TestCase
from django.template.loader import get_template
from django.template import Context, Template

from mashup.views import Mashup, HTMLView, ViewView, URLView, TOKEN_LENGTH


class DummyRequest(object):
    user = ""


class DummyGetRequest(DummyRequest):
    method = "GET"


class DummyPostRequest(DummyRequest):
    method = "POST"


class DummyDeleteRequest(DummyRequest):
    method = "DELETE"


class MyMashup(Mashup):
    views = [HTMLView("<p>This is a bunch of html<p>", container="mashup/test/first_test_container.html"),
             HTMLView("<p>This is another bunch of html</p>", container="mashup/test/second_test_container.html"),
             ]


class MySecondMashup(Mashup):
    views = [ViewView(MyMashup, container="mashup/test/third_test_container.html"),
             HTMLView("<p>A third bunch of HTML</p>"),
             ]


class MyThirdMashup(Mashup):

    views = [URLView("/testing/url", container="mashup/test/third_test_container.html"),
             URLView("/test/url"),
             ]


class MyMashupContained(MyMashup):
    containers = ("mashup/test/fourth_test_container.html",
                  "mashup/test/fifth_test_container.html",)


class MySecondMashupContained(MySecondMashup):
    containers = ("mashup/test/sixth_test_container.html",
                  "mashup/test/seventh_test_container.html")


class MyGetPostMashup(Mashup):
    get_views = MyMashup.views
    post_views = MySecondMashup.views


class MyGetPostMashupContained(Mashup):
    get_views = MyMashup.views
    post_views = MySecondMashup.views

    get_containers = MyMashupContained.containers
    post_containers = MySecondMashupContained.containers


class MashupViewTests(TestCase):

    def test_html_view_mashing(self):
        # print(MyMashup.as_view()(DummyGetRequest()).content)
        #                  b"<div class='first-mash'><p>This is a bunch of html<p></div><div class='first-mash'><p>This is another bunch of html</p></div>"
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
            this_template = get_template(view.template_name)

            context = Context({
                "url": view.content,
                "token": dummy_token
            })

            target_length += len(this_template.render(context))

            if hasattr(view, "container") and view.container:
                target_length += len(get_template(view.container).render(Context()))

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

    def test_mashup_containers(self):

        self.assertEqual(MyMashupContained.as_view()(DummyGetRequest()).content,
                         b"<div id=first-view-container><div class='first-mash'><p>This is a bunch of html<p></div></div><div id=second-view-container><div class='second-mash'><p>This is another bunch of html</p></div></div>")

        self.assertEqual(MySecondMashupContained.as_view()(DummyGetRequest()).content,
                         b"<div id=first-second-view-container><div class='big-mash-container'><div class='first-mash'><p>This is a bunch of html<p></div><div class='second-mash'><p>This is another bunch of html</p></div></div></div><div id=second-second-view-container><p>A third bunch of HTML</p></div>")


class MashupGetVsPost(TestCase):

    def test_get_vs_post_views(self):

        # Assert that MyGetPostMashup gives the correct response to a GET
        self.assertEqual(MyGetPostMashup.as_view()(DummyGetRequest()).content,
                         b"<div class='first-mash'><p>This is a bunch of html<p></div><div class='second-mash'><p>This is another bunch of html</p></div>")

        # Assert that MyGetPostMashup gives the correct response to a POST
        self.assertEqual(MyGetPostMashup.as_view()(DummyPostRequest()).content,
                         b"<div class='big-mash-container'><div class='first-mash'><p>This is a bunch of html<p></div><div class='second-mash'><p>This is another bunch of html</p></div></div><p>A third bunch of HTML</p>")

        # Assert that MyGetPostMashup gives the correct response to a DELETE
        self.assertEqual(MyGetPostMashup.as_view()(DummyDeleteRequest()).content, b"")

    def test_get_vs_post_containers(self):
        self.assertEqual(MyGetPostMashupContained.as_view()(DummyGetRequest()).content,
                         b"<div id=first-view-container><div class='first-mash'><p>This is a bunch of html<p></div></div><div id=second-view-container><div class='second-mash'><p>This is another bunch of html</p></div></div>")

        self.assertEqual(MyGetPostMashupContained.as_view()(DummyPostRequest()).content,
                         b"<div id=first-second-view-container><div class='big-mash-container'><div class='first-mash'><p>This is a bunch of html<p></div><div class='second-mash'><p>This is another bunch of html</p></div></div></div><div id=second-second-view-container><p>A third bunch of HTML</p></div>")

