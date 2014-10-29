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
                 URLView(reverse('account:login')),
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

Each component class takes an optional container keyword argument. This should be a template name. Use '{{ mashup|safe }}' to specify where the content should be placed:

``` 
    from django.core.urlresolvers import reverse
    from mashup.views import MashUp, URLView, HTMLView
    
    class MyMashup(MashUp):
        views = [HTMLView("Use the following form to log in.",
                          container="my_app/my_template.html"),
                 URLView(reverse('account:login'),
                ]
                
    .
    .
    .
    # my_app/my_template.html
    
    <div class=explanation>{{ mashup|safe }}</div>
```

The three component classes may be subclassed with default containers. The following MyMashup class will produce the same response as the one above:

```
    from django.core.urlresolvers import reverse
    from mashup.views import MashUp, URLView, HTMLView
    
    class MyHTMLView(HTMLView):
        container = "my_app/my_template.html"
    
    class MyMashup(MashUp):
        views = [MyHTMLView("Use the following form to log in."),
                 URLView(reverse('account:login'),
                ]  
```

The Mashup class may also be given default containers. Here's an abstract subclass of Mashup which takes two views and wraps them in the the divs #left-pane and #right-pane. Any Mashups which inherit from this Mashup will have their views contained in those divs:

```
    from mashup.views import MashUp
    
    class MyPaneMashup(Mashup):
        containers = ('my_app/my_right_pane.html',
                      'my_app/my_left_pane.html',
                     )
                     
    .
    .
    .
    # my_app/my_right_pane.html
    
    <div id=right-pane>{{ mashup|safe }}</div>
    .
    .
    .
    
    # my_app/my_left_pane.html
    
    <div id=right-pane>{{ mashup|safe }}</div>

```

Finally, you may define Mashup views and containers by request method: prefix 'views' or 'containers' with the lowercase name of the request method. For example, if your form views respond via Ajax to POST requests, then you do not want your Mashup to attach HTML to the request:

```
from mashup.views import Mashup

...

class MyFormMashup(Mashup):
    get_views = (MyAjaxFormView,
                 HTMLView("<p>Words words words.</p>", container="my_app/my_template.html"),
                )
    get_containers = ('my_app/my_right_pane.html',
                      'my_app/my_right_pane.html',)
                      
    post_views = (MyAjaxFormView,)
    post_containers = ()
```

Notes
=====
If you use a custom jquery or javascript function for loading page content via Ajax, you can specify that function in a subclass of URLView. See views.py.

If you find the use of placeholder strings like "{{ mashup }}" uncouth, you can redifine them in a single line in views.py.

django-mashup is almost certainly not compatible with Python 2.x, due to its handling of bytestrings, but probably could be made compatible with Python 2.x.

Getting Involved
================

Feel free to open pull requests or issues. GitHub is the canonical location of this project.

I am particularly interested in other people's thoughts on the most appropriate way to provide view context to the HTMLView, so that it can be rendered with context.
