import string
import random

try:
    # Python 2
    from itertools import izip_longest as zip_longest
except ImportError:
    # Python 3
    from itertools import zip_longest

from django.views.generic import View
from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.shortcuts import render

TOKEN_LENGTH = 20
MASHUP_CONTEXT_VARIABLE_NAME = "mashup"

JS_JQUERY_AJAX_LOADER_TEMPLATE_NAME = "mashup/js_jquery_ajax_loader.html"


class Mashup(View):

    containers = ()
    views = ()

    def dispatch(self, request, *args, **kwargs):
        response = b""

        request_method = request.method.lower()

        these_containers = getattr(self, request_method + "_containers") if request_method + "_containers" in dir(self) else self.containers
        these_views = getattr(self, request_method + "_views") if request_method + "_views" in dir(self) else self.views

        for view, container in zip_longest(these_views, these_containers, fillvalue=None):
            this_response = view.dispatch(request, *args, **kwargs).content
            if container:
                this_response = render(request, container, {"mashup": this_response}).content
            response += this_response

        return HttpResponse(response)


class MashupView(object):
    """
    Parent class for component views of a Mashup

    All subclasses should define a content attribute.
    All subclasses may define an optional container attribute, which must include the string "{{ mashup }}"
    The string "{{ mashup }}" in the container will be replaced with the content produced
    """

    def __init__(self, content, **kwargs):
        self.content = content
        if "container" in kwargs:
            self.container = kwargs["container"]

    def content_containment(self, request, content):
        if hasattr(self, "container") and self.container:

            content = render(request, self.container, {MASHUP_CONTEXT_VARIABLE_NAME: content})

        return content


class HTMLView(MashupView):
    """
    Mashup component for viewing raw html

    Subclasses should define a content attribute: string of HTML
    """

    def dispatch(self, request, *args, **kwargs):
        return HttpResponse(self.content_containment(request, self.content))


class URLView(MashupView, TemplateView):
    """
    Mashup component for loading a url via ajax
    Tries to use jquery's load()
    Will use a javascript alternative if jquery is unavailable
    Confirm that this works on your target clients
    Replace the default js/jquery loader by providing your own mashup/js_jquery_ajax_loader.html template

    Subclasses should define a content attribute: a url string
    """

    template_name = JS_JQUERY_AJAX_LOADER_TEMPLATE_NAME

    def get_context_data(self, **kwargs):
        context = super(URLView, self).get_context_data(**kwargs)
        context["token"] = ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(TOKEN_LENGTH))
        context["url"] = self.content

        return context

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        response = super(URLView, self).dispatch(request, *args, **kwargs)
        response.render()

        return HttpResponse(self.content_containment(request, response.content))


class ViewView(MashupView):
    """
    Mashup component for viewing a view

    Subclasses should define a content attribute: a subclass of django's view
    """

    def dispatch(self, request, *args, **kwargs):
        response = self.content.as_view()(request, *args, **kwargs)
        if hasattr(response, "render"):
            response.render()
        response.content = self.content_containment(request, response.content)
        return response