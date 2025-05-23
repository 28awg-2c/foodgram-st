from django.http import HttpResponse


def about(request):
    return HttpResponse("Страница 'О проекте'")


def tech(request):
    return HttpResponse("Страница 'Технологии'")
