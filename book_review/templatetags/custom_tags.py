from django.urls import reverse
from urllib.parse import urlencode
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Replaces value of url parameter (such as page=value in pagination).
    """
    query = context.get('request').GET.copy()
    query.update(kwargs)
    return urlencode(query)


@register.simple_tag(takes_context=True)
def url_next(context, **kwargs):
    """
    If 'Login' or 'Sign up' buttons are pressed, current path is captured in 'next' parameter,
    so user will be redirected back to his last page after login or registration.
    Exception is case where previous page is login page or registration page.
    In this case user will be redirected to index page, so it prevents looping.
    Same about 'Logout'. User stays at page he was before pressing 'Logout' button.
    Exception is 'My reviews' page. Only authenticated users have access to it,
    so after logout user is redirected to index page.
    """
    cur_path = context.get('request').path

    if cur_path not in [reverse('users:login'), reverse('users:register'), reverse('book_review:my_reviews')]:
        return '?' + urlencode(kwargs)
    else:
        return ''


@register.simple_tag(takes_context=True)
def get_page_range(context, on_each_side=2, on_ends=1):
    """
    Allows to call 'get_elided_page_range' method directly from template.
    """
    cur_page = context.get('page_obj').number
    page_range = context.get('paginator').get_elided_page_range(cur_page, on_each_side=on_each_side, on_ends=on_ends)

    return page_range
