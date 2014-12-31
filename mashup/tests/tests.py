from django.test import TestCase
from django.template.loader import get_template
from django.template import Context

from mashup.views import Mashup, ViewMash, URLMash, TOKEN_LENGTH, TemplateMash


class DummyRequest(object):
    user = ""
    path = "/"


class DummyGetRequest(DummyRequest):
    method = "GET"


class DummyPostRequest(DummyRequest):
    method = "POST"


class DummyDeleteRequest(DummyRequest):
    method = "DELETE"


class MyMashup(Mashup):
    views = [TemplateMash("mashup/test/first_test_content.html",
                          container="mashup/test/first_test_container.html"),
             TemplateMash("mashup/test/second_test_content.html",
                          container="mashup/test/second_test_container.html"),
             ]


class MySecondMashup(Mashup):
    views = [ViewMash(MyMashup, container="mashup/test/third_test_container.html"),
             TemplateMash("mashup/test/third_test_content.html"),
             ]


class MyThirdMashup(Mashup):

    views = [URLMash("/testing/url", container="mashup/test/third_test_container.html"),
             URLMash("/test/url"),
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

    def test_template_mashing(self):
        # Assert that MyMashup gives the expected response
        self.assertEqual(MyMashup.as_view()(DummyGetRequest()).content,
                         b"<div class='first-mash'><p>This is a bunch of html<p></div><div class='second-mash'><p>This is another bunch of html</p></div>")

    def test_view_view_mashing(self):
        # This test might fail because of a failure in TemplateMash
        # If both this test and test_template_mashing fails, address test_template_mashing first

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

        class MyTemplateMash(TemplateMash):
            container = "test_container"

        templatemash = TemplateMash("some content")
        mytemplatemash = MyTemplateMash("some content")
        mysecondtemplatemash = MyTemplateMash("some content", container="test_container_2")

        # Assert that the instance of TemplateMash has no container
        self.assertTrue((not hasattr(templatemash, "container")) or (not templatemash.container))
        # Assert that the first instance of MyTemplateMash has the container we gave it.
        self.assertEqual(mytemplatemash.container, "test_container")
        # Assert that the second instance of MyTemplateMash has the container we gave it.
        self.assertEqual(mysecondtemplatemash.container, "test_container_2")

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

