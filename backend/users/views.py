import jwt
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import UserProfile, UserActivity



def login(request):
    username = request.GET.get('user')
    password = request.GET.get('pass')

    user = authenticate(username=username, password=password)
    
    # Verificar si la autenticación fue exitosa
    if user is not None:
        # Usuario autenticado, generando token JWT
        payload = {
            'username': user.username,
            'firstname': user.first_name,
            'lastname': user.last_name,
            'staff': user.is_staff
        }
        # Genera el token JWT con una clave secreta (debes cambiar esta clave por una más segura)
        token = jwt.encode(payload, 'inamhi_geoglows_drs2787', algorithm='HS256')
        # Retorna el token como respuesta
        return JsonResponse({'token': token})
    else:
        # Usuario no autenticado
        return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
    



# ?email=juchancay@gmail.com&pass=JuSS123&firstname=Enrique&lastname=Sanchez&institution=INAMHI&position=hidrologo
def register(request):
    try:
        # Obtén los datos del formulario
        username = request.GET.get('email')
        password = request.GET.get('pass')
        firstname = request.GET.get('firstname')
        lastname = request.GET.get('lastname')
        email = request.GET.get('email')
        institution = request.GET.get('institution')
        position = request.GET.get('position')

        # Crea un nuevo usuario
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password, 
            first_name=firstname, 
            last_name=lastname)

        # Crea un UserProfile asociado al usuario
        UserProfile.objects.create(user=user, institution=institution, position=position)

        # Opcional: Crea un UserActivity asociado al usuario 
        UserActivity.objects.create(user=user, date=datetime.now(), activity='Registered')
    except:
        return JsonResponse({'status': 'error'})
    
    return JsonResponse({'status': 'success'})