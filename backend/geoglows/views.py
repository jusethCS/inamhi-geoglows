import rasterio
from django.http import HttpResponse

ENDPOINT = "/usr/share/geoserver/data_dir/data" 


def download_from_geoserver(workspace, layer):
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



def download_daily_precipitaion(request):
    return download_from_geoserver("fireforest", "daily_precipitation")