from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import simplejson


def create_photo(request):
    # request.meta.contenttype = 'application/x-www-form-urlencoded; charset=utf-8'
    if request.method == 'POST':
        dic = simplejson.loads(request.body)
        return HttpResponse(simplejson.dumps(dic), mimetype='application/json')

    return render_to_response('tests/create_photo.html', context_instance=RequestContext(request))