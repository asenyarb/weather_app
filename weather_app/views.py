from django.shortcuts import render
import requests
from .models import City
from .forms import CityForm

# Create your views here.


def index(request):
    appid = 'd5690ce2c8cf4f332eb7788636e9bc69'
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=' + appid

    if request.method == 'POST':
        if request.POST.get("city_name"):
            # POST message from add-city form
            form = CityForm(request.POST)
            if len(City.objects.all()) > 5:
                text_message = r"Too many cities in list! Delete some of to continue."
            else:
                if not form.is_valid():
                    text_message = r"The city wasn't saved because the form isn't valid!"
                else:
                    model = form.save(commit=False)     # Save form into temporary model
                    if City.objects.filter(city_name=model.city_name).count():  # Check if city already exists in DB
                        text_message = r"The city is already in list!"
                    else:
                        if requests.get(url.format(model.city_name)).json()['cod'] == '404':    # Request error
                            text_message = r"The city wasn't found!"
                        else:
                            form.save()
        else:
            # POST message from delete button
            string = 'delete_{}'
            for city in City.objects.all():
                if string.format(city.city_name) in request.POST:   # Searching for button name
                    City.objects.filter(city_name=city.city_name).delete()
    form = CityForm()
    cities = City.objects.all()
    info = []
    for city in cities:
        response = requests.get(url.format(city.city_name)).json()
        city_info = {
            'city_name': response['name'],
            'temp': response['main']['temp'],
            'temp_min': response['main']['temp_min'],
            'temp_max': response['main']['temp_max'],
            'humidity': response['main']['humidity'],
            'weather': response['weather'][0]['main'],
            'icon_id': response['weather'][0]['icon'],
        }
        info.append(city_info)
    try:
        result = render(request, 'index.html', {'all_info': info, 'form': form, 'message': text_message})
    except NameError:   # Text_message is accessed before assignment(is blank)
        result = render(request, 'index.html', {'all_info': info, 'form': form})
    return result
