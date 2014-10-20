django-mashup
=============

django-mashup is a view masher for the Django Framework. Combine multiple views, strings of HTML, and/or ajax loaded urls into a single view

Installation
===============

Install the module in your Python distribution or virtualenv::

    $ pip install git+https://github.com/SigmaEducation/django-mashup.git

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

    from mashup.views import URLView, HTMLView, ViewView
    
Example:

``` 
    from django.core.urlresolvers import reverse
    from mashup.views import MashUp, URLView, HTMLView
    
    class MyMashup(MashUp):
        views = [HTMLView("Use the following form to log in."),
                 URLView(reverse('account:login'),
                ]
```

Here's an example that mashes a view with HTML:

``` 
    from django.views.generic.base import TemplateView
    from mashup.views import MashUp, HTMLView, ViewView
    
    class MyTemplateView(TemplateView):
        template_name = 'cool_stuff.html'
    
    class MyMashup(MashUp):
        views = [HTMLView('Use the following form to log in.'),
                 ViewView(MyTemplateView),
                ]
```

Each component class takes an optional container keyword argument. Use the a '{{ mashup }}' to specify where the content should be placed:

``` 
    from django.core.urlresolvers import reverse
    from mashup.views import MashUp, URLView, HTMLView
    
    class MyMashup(MashUp):
        views = [HTMLView("Use the following form to log in.",
                          container="<div class=explanation>{{ mashup }}</div>"),
                 URLView(reverse('account:login'),
                ]
```

The three component classes may be subclassed with default containers. The following MyMashup class will produce the same response as the one above:

```
    from django.core.urlresolvers import reverse
    from mashup.views import MashUp, URLView, HTMLView
    
    class MyHTMLView(HTMLView):
        container = "<div class=explanation>{{ mashup }}</div>"
    
    class MyMashup(MashUp):
        views = [MyHTMLView("Use the following form to log in."),
                 URLView(reverse('account:login'),
                ]  
```

Also, URLView may be subclassed with custom javascript/jquery loading strings.

Notes
=====

If you find the use of placeholder strings like "{{ mashup }}" uncouth, you can redifine them in a single line in views.py.

django-mashup is almost certainly not compatible with Python 2.x, due to its handling of bytestrings, but probably could be made compatible with Python 2.x.

Getting Involved
================

Feel free to open pull requests or issues. GitHub is the canonical location of this project.

I am particularly interested in other people's thoughts on the most appropriate way to provide view context to the HTMLView, so that it can be rendered with context.
