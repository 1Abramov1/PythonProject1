from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Мой Django проект работает!</h1><p>Поздравляю!</p>")
