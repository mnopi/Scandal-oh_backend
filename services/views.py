from django.http.response import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from services.fileService import FileService


def create_photo(request):
    """
    id_usuario, imagen, titulo, categoria
    """



    # if request.method == 'POST' or request.method == 'DELETE':
    #     fileUploadHandler(request, 'photo', id)
    #
    return render_to_response('form.html', context_instance=RequestContext(request))



def fileUploadHandler(request, resource, id):
    """
    /services/[resource]/[id]/file

    e.g.: /services/photo/16/file
    """
    service = FileService(request, resource, id)

    if request.method == 'POST':
        try:
            for uploaded_file in request.FILES.items():
                service.upload_file(uploaded_file[1])
        except:
            raise Exception

    elif request.method == 'DELETE':
        return service.delete_file()