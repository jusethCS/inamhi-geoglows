import rasterio
from django.http import HttpResponse

ENDPOINT = "/usr/share/geoserver/data_dir/data" 

def download(request):
    workspace = "fireforest"#request.GET.get('workspace')
    layer = "daily_precipitation"#request.GET.get('layer')
    file_path = f'{ENDPOINT}/{workspace}/{layer}/{layer}.geotiff'
    try:
        with rasterio.open(file_path) as dataset:
            response = HttpResponse(open(file_path, 'rb').read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename={workspace}-{layer}'
            return response
    except FileNotFoundError:
        return HttpResponse('File not found', status=404)
    except Exception as e:
        return HttpResponse(f'Error processing file: {e}', status=500)