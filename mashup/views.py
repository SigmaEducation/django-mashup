import string
import random
from itertools import zip_longest

from django.views.generic import View
from django.http import HttpResponse

TOKEN_LENGTH = 20
CONTENT_SUB_STRING = "{{ mashup }}"
ENCODING_METHOD = 'utf-8'

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


class MashupView():
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


class URLView(MashupView):
    """
    Mashup component for loading a url via ajax
    Tries to use jquery's load()
    Will use a javascript alternative if jquery is unavailable
    Confirm that this works on your target clients

    Subclasses should define a content attribute: a url string
    """

    url_sub_string = "{{ url }}"
    token_sub_string = "{{ token }}"

    jquery_loader = "$( this_element ).load( this_url );"
    javascript_loader = """
    req = new XMLHttpRequest();
    req.open("GET", this_url, false);
    req.send(null);

    this_element.innerHTML = req.responseText;
    """

    jquery_detector = """
        <div id='""" + token_sub_string + """'></div>
        <script>
            var this_element = document.getElementById('""" + token_sub_string + """')
            var this_url = '""" + url_sub_string + """'
            if (typeof jQuery !== 'undefined') {
                %s
            } else {
                %s
            }
        </script>
        """

    def dispatch(self, request, *args, **kwargs):
        response = self.jquery_detector % (self.jquery_loader, self.javascript_loader)
        response = response.replace(self.token_sub_string, ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(TOKEN_LENGTH)))
        response = response.replace(self.url_sub_string, self.content)

        return HttpResponse(self.content_containment(response))


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