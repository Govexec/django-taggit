from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from cachecow.pagecache import cache_page

from taggit.models import Tag, TaggedItem

@cache_page
def ajax(request):
    ''' get all of the tags available and return as a json array'''
    data = serializers.serialize(
        'json', Tag.objects.order_by('slug').all(), fields=('name'),
        ensure_ascii=False
    )

    return HttpResponse(data)

def tagged_object_list(request, slug, queryset, **kwargs):
    if callable(queryset):
        queryset = queryset()
    tag = get_object_or_404(Tag, slug=slug)
    qs = queryset.filter(pk__in=TaggedItem.objects.filter(
        tag=tag, content_type=ContentType.objects.get_for_model(queryset.model)
    ).values_list("object_id", flat=True))
    if "extra_context" not in kwargs:
        kwargs["extra_context"] = {}
    kwargs["extra_context"]["tag"] = tag
    return ListView.as_view(request, qs, **kwargs)

def media(request, path):
    from django.views.static import serve
    from taggit.settings import TAGGIT_MEDIA_DIR
    return serve(request, path, TAGGIT_MEDIA_DIR)
