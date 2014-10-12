import string
import random

from django.views.generic import View
from django.http import HttpResponse

TOKEN_LENGTH = 20


class Mashup(View):

    def dispatch(self, request, *args, **kwargs):
        response = b""
        for view in self.views:
            response += view.dispatch(request, *args, **kwargs).content

        return HttpResponse(response)


class MashupView():
    """
    Parent class for component views of a Mashup

    All subclasses should define a content attribute.
    All subclasses may define an optional container attribute, which must include the string "{{ mashup }}"
    The string "{{ mashup }}" in the container will be replaced with the content produced
    """

    CONTENT_SUB_STRING = "{{ mashup }}"

    def __init__(self, content, **kwargs):
        self.content = content
        if "container" in kwargs:
            self.container = kwargs["container"]

    def content_containment(self, content):
        if hasattr(self, "container") and self.container:
            if isinstance(content, str):
                return self.container.replace(self.CONTENT_SUB_STRING, content)
            else:
                return bytes(self.container, 'utf-8').replace(bytes(self.CONTENT_SUB_STRING, 'utf-8'), content)

        return content


class HTMLView(MashupView):
    """
    Mashup component for viewing raw html

    Subclasses should define a content attribute: string of HTML
    """

    def dispatch(self, request):
        return HttpResponse(self.content_containment(self.content))


class URLView(MashupView):
    """
    Mashup component for loading a url via ajax
    Tries to use jquery's load()
    Will use a javascript alternative if jquery is unavailable
    Confirm that this works on your target clients

    Subclasses should define a content attribute: a url string
    """

    URL_SUB_STRING = "{{ url }}"
    TOKEN_SUB_STRING = "{{ token }}"

    jquery_loader = "$( this_element ).load( this_url );"
    javascript_loader = """
    req = new XMLHttpRequest();
    req.open("GET", this_url, false);
    req.send(null);

    this_element.innerHTML = req.responseText;
    """

    jquery_detector = """
        <div id='""" + TOKEN_SUB_STRING + """'></div>
        <script>
            var this_element = document.getElementById('""" + TOKEN_SUB_STRING + """')
            var this_url = '""" + URL_SUB_STRING + """'
            if (typeof jQuery !== 'undefined') {
                %s
            } else {
                %s
            }
        </script>
        """

    def dispatch(self, request):
        response = self.jquery_detector % (self.jquery_loader, self.javascript_loader)
        response = response.replace(self.TOKEN_SUB_STRING, ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(TOKEN_LENGTH)))
        response = response.replace(self.URL_SUB_STRING, self.content)

        return HttpResponse(self.content_containment(response))


class ViewView(MashupView):
    """
    Mashup component for viewing a view

    Subclasses should define a content attribute: a subclass of django's view
    """

    def dispatch(self, request):
        response = self.content.as_view()(request)
        if hasattr(response, "render"):
            response.render()
        response.content = self.content_containment(response.content)
        return response