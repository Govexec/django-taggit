import os
from __future__ import unicode_literals

from django import forms
from django.utils import six
from django.utils.translation import ugettext as _

from taggit.utils import clean_tag_string, edit_string_for_tags, parse_tags


class TagWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        if value is not None and not isinstance(value, six.string_types):
            value = edit_string_for_tags([
                o.tag for o in value.select_related("tag")])

        if attrs is None:
            attrs = {}
        attrs.update({'class': 'taggit-tags'})
        return super(TagWidget, self).render(name, value, attrs)


    def get_media(self):
        """
        A method used to dynamically generate the media property, since we may
        not have the urls ready at the time of import, and then the reverse()
        call would fail.
        """
        from django.forms.widgets import Media as _Media
        from django.core.urlresolvers import NoReverseMatch, reverse

        try:
            media_url = reverse('taggit-static', kwargs={'path': ''})
        except NoReverseMatch:
            media_url = None

        if media_url is None:
            class_props = {}
        else:
            class_props = {
                'css': {
                    'all': (
                        os.path.join(media_url, 'css', 'autocomplete.css'),
                    )
                },
                'js': (
                    os.path.join(media_url, 'js', 'taggit.js'),
                )
            }
            media_cls = type('Media', (_Media,), class_props)
        return _Media(media_cls)

    media = property(get_media)

    def _has_changed(self, initial, data):
        """
        Whether the input value has changed. Used for recording in
        django_admin_log.

        Because initial is passed as a queryset, and data is a string, we need
        to turn the former into a string and run the latter through a function
        which cleans it up and sorts the tags in it.
        """
        if initial is None:
            initial = ""
        elif hasattr(initial, 'select_related'):
            initial_vals = [o.tag for o in initial.select_related("tag")]
            initial = edit_string_for_tags(initial_vals)
        else:
            try:
                if len(initial) == 0:
                    initial = ""
                else:
                    initial = edit_string_for_tags(initial)
            except TypeError, ValueError:
                initial = ""
        data = clean_tag_string(data)
        return super(TagWidget, self)._has_changed(initial, data)


class TagField(forms.CharField):
    widget = TagWidget

    def clean(self, value):
        value = super(TagField, self).clean(value)
        try:
            return parse_tags(value)
        except ValueError:
            raise forms.ValidationError(
                _("Please provide a comma-separated list of tags."))
