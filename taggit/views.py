from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.core import serializers
from django.http import HttpResponse
from cachew.decorators import cache_page_function as cache_page

from taggit.models import TaggedItem, Tag

@cache_page(900)
def ajax(request):
	''' get all of the tags available and return as a json array'''
	data = serializers.serialize('json', Tag.objects.order_by('slug').all(),
		fields=('name'), ensure_ascii=False)
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
    return object_list(request, qs, **kwargs)

def media(request, path):
	from django.views.static import serve
	from taggit.settings import TAGGIT_MEDIA_DIR
	return serve(request, path, TAGGIT_MEDIA_DIR)
