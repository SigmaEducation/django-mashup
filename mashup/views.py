import string
import random
from itertools import zip_longest

from django.views.generic import View
from django.views.generic.base import TemplateView
from django.http import HttpResponse

TOKEN_LENGTH = 20
CONTENT_SUB_STRING = "{{ mashup }}"
ENCODING_METHOD = 'utf-8'

JS_JQUERY_AJAX_LOADER_TEMPLATE_NAME = "mashup/js_jquery_ajax_loader.html"


class Mashup(View):

    containers = ()
    views = ()
    
    encoding_method = ENCODING_METHOD
    content_sub_string = CONTENT_SUB_STRING

    def dispatch(self, request, *args, **kwargs):
        response = b""

        request_method = request.method.lower()

        these_containers = getattr(self, request_method + "_containers") if request_method + "_containers" in dir(self) else self.containers
        these_views = getattr(self, request_method + "_views") if request_method + "_views" in dir(self) else self.views

        for view, container in zip_longest(these_views, these_containers, fillvalue=None):
            this_response = view.dispatch(request, *args, **kwargs).content
            if container:
                this_response = bytes(container, 'utf-8').replace(self.content_sub_string_bytes, this_response)
            response += this_response

        return HttpResponse(response)
    
    @property
    def content_sub_string_bytes(self):
        if not hasattr(self, "_content_sub_string_bytes"):
            self._content_sub_string_bytes = bytes(self.content_sub_string, self.encoding_method)
            
        return self._content_sub_string_bytes


class MashupView(object):
    """
    Parent class for component views of a Mashup

    All subclasses should define a content attribute.
    All subclasses may define an optional container attribute, which must include the string "{{ mashup }}"
    The string "{{ mashup }}" in the container will be replaced with the content produced
    """

    content_sub_string = CONTENT_SUB_STRING
    encoding_method = ENCODING_METHOD

    def __init__(self, content, **kwargs):
        self.content = content
        if "container" in kwargs:
            self.container = kwargs["container"]

    def content_containment(self, content):
        if hasattr(self, "container") and self.container:
            if isinstance(content, str):
                return self.container.replace(self.content_sub_string, content)
            else:
                return bytes(self.container, self.encoding_method).replace(bytes(self.content_sub_string, self.encoding_method), content)

        return content


class HTMLView(MashupView):
    """
    Mashup component for viewing raw html

    Subclasses should define a content attribute: string of HTML
    """

    def dispatch(self, request, *args, **kwargs):
        return HttpResponse(self.content_containment(self.content))


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

        return HttpResponse(self.content_containment(response.content))


class ViewView(MashupView):
    """
    Mashup component for viewing a view

    Subclasses should define a content attribute: a subclass of django's view
    """

    def dispatch(self, request, *args, **kwargs):
        response = self.content.as_view()(request, *args, **kwargs)
        if hasattr(response, "render"):
            response.render()
        response.content = self.content_containment(response.content)
        return response