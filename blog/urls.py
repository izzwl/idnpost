from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('',views.home,name='home'),
    path('contact',views.contact,name='contact'),
    path('subscribe',views.subscribe,name='subscribe'),
    path('<slug:category>',views.categorized,name='category'),
    path('<slug:category>/<slug:post>',views.read_post,name='read_post'),
]