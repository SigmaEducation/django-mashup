[![Downloads](https://pypip.in/download/django-mashup/badge.svg)](https://pypi.python.org/pypi/django-mashup/)
django-mashup
=============

django-mashup is a view masher for the Django Framework. Combine multiple views, templates, and/or Ajax loaded urls into a single class-based view.

Wrap those views in template-based containers.

Define different combinations of views and/or containers for different request types.

Installation
===============

Install the module in your Python distribution or virtualenv::

    $ pip install django-mashup

Add the application to your `INSTALLED_APPS`::

```
  INSTALLED_APPS = (...
  "mashup",
  ...
  )
```

Use
===

django-mashup provides one view class:

    from mashup.views import MashUp
    
and three component classes:

    from mashup.views import URLMash, TemplateMash, ViewMash
    
Example:

``` 
    from django.core.urlresolvers import reverse
    from mashup.views import MashUp, URLMash, TemplateMash
    
    class MyMashup(MashUp):
        views = [TemplateMash("my_app/my_login_instructions.html"),
                 URLMash(reverse('account:login')),
                ]
                
    # my_app/my_login_instructions.html
    
    <p>Use the following form to log in.</p>
```

Here's an example that mashes a view with HTML:

``` 
    from django.views.generic.edit import FormView
    from mashup.views import MashUp, TemplateMash, ViewMash
    
    class MyFormView(FormView):
        ...
    
    class MyMashup(MashUp):
        views = [TemplateMash("my_app/my_login_instructions.html"),
                 ViewMash(MyFormView),
                ]
```

Each component class takes an optional container keyword argument. This should be a template name. Use '{{ mashup|safe }}' to specify where the content should be placed:

``` 
    from django.core.urlresolvers import reverse
    from mashup.views import MashUp, URLMash, TemplateMash
    
    class MyMashup(MashUp):
        views = [TemplateMash("my_app/my_login_instructions.html",
                              container="my_app/my_template.html"),
                 URLMash(reverse('account:login')),
                
    ...
    
    # my_app/my_template.html
    
    <div class=explanation>{{ mashup|safe }}</div>
```

The three component classes may be subclassed with default containers. The following MyMashup class will produce the same response as the one above:

```
    from django.core.urlresolvers import reverse
    from mashup.views import MashUp, URLMash, TemplateMash
    
    class MyTemplateMash(TemplateMash):
        container = "my_app/my_template.html"
    
    class MyMashup(MashUp):
        views = [MyTemplateMash("my_app/my_login_instructions.html"),
                 URLMash(reverse('account:login')),
                ]  
```

The Mashup class may also be given default containers. Here's an abstract subclass of Mashup which takes two views and wraps them in the the divs #left-pane and #right-pane. Any Mashups which inherit from this Mashup will have their views contained in those divs:

```
    from mashup.views import MashUp
    
    class MyPaneMashup(Mashup):
        containers = ('my_app/my_right_pane.html',
                      'my_app/my_left_pane.html',
                     )
                     
    ...
    
    # my_app/my_right_pane.html
    
    <div id=right-pane>{{ mashup|safe }}</div>
    
    ...
    
    # my_app/my_left_pane.html
    
    <div id=right-pane>{{ mashup|safe }}</div>

```

Finally, you may define Mashup views and containers by request method: prefix 'views' or 'containers' with the lowercase name of the request method.

For example, your form views might respond with HTML to GET requests and JSON to POST requests; in this case you do not want your Mashup to attach HTML containers and content to POST response:

```
from mashup.views import Mashup, TemplateMash

from myapp.views import MyAjaxFormView


class MyFormMashup(Mashup):
    get_views = (MyAjaxFormView,
                 TemplateMash("my_app/my_login_instructions.html", container="my_app/my_template.html"),
                )
    get_containers = ('my_app/my_right_pane.html',
                      'my_app/my_right_pane.html',)
                      
    post_views = (MyAjaxFormView,)
    post_containers = ()
```
You may similarly define unique DELETE, PUT, TRACE, etc., views/containers.

Compatibility
=============

* Django 1.7
* Python 2.7, 3.4

Notes
=====
If you use a custom jquery or javascript function for loading page content via Ajax, you can specify that function by providing your own /templates/mashup/js_jquery_ajax_loader.html.


Getting Involved
================

Feel free to open pull requests or issues. GitHub is the canonical location of this project.
