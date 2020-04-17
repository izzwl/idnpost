from django.shortcuts import render
from django.db.models import Q
from django.contrib import messages
from django.core.validators import validate_email
from django.http import Http404,HttpResponse,JsonResponse
from .models import Post,Category,Tag,ViewerMessage,Subscriber,Setting
from .forms import ViewerMessageForm
# Create your views here.
def get_category(request):
    filter = {
        'is_active':True,
    }
    order = ['pk',]
    categories = Category.objects.all().order_by(*order)
    return categories
def get_setting(request):
    setting = Setting.objects.all()
    return {s.name:s.value for s in setting}

def home(request,template_name='web/home.html'):
    active_post = Post.objects.select_related('writer','category',).prefetch_related('tags').filter(is_active=True)
    context = {
        'settings':get_setting(request),
        'categories':get_category(request),
        'carousels':active_post.filter(is_picked=True),
        'recent_posts':active_post.order_by('-dt_add')[:5],
        'popular_posts':active_post.order_by('-total_view')[:9],
    }
    return render(request,template_name,context)

def categorized(request,category,template_name='web/category.html'):
    try:
        category = Category.objects.get(url=category)
    except:
        return HttpResponse(status=404)
    active_post = Post.objects.select_related('writer','category',).prefetch_related('tags')\
        .filter(Q(is_active=True) and Q( Q(category=category) or Q(categories=category) ))\
        .distinct()
    context = {
        'settings':get_setting(request),
        'category':category,
        'categories':get_category(request),
        'recent_posts':active_post.order_by('-dt_add')[:5],
        'popular_posts':active_post.order_by('-total_view')[:9],
    }
    return render(request,template_name,context)

def read_post(request,category,post,template_name='web/read_post.html'):
    try:
        category = Category.objects.get(url=category)
    except:
        return HttpResponse(status=404)
    try:
        post = Post.objects.select_related('writer','category',).prefetch_related('tags').get(url=post)
    except:
        return HttpResponse(status=404)    
    
    active_post = Post.objects.select_related('writer','category',).prefetch_related('tags')\
        .filter(Q(is_active=True) and Q( Q(category=category) or Q(categories=category) ))\
        .distinct()

    context = {
        'settings':get_setting(request),
        'category':category,
        'post':post,
        'categories':get_category(request),
        'related_posts':active_post.order_by('-total_view')[:5],
    }
    return render(request,template_name,context)

def contact(request,template_name='web/contact.html'):
    msg = {
        'success':'Your message has been sent, thanks ;)',
        'error':'Oops..Something wrong',
    }
    form = ViewerMessageForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save()
            messages.add_message(request,messages.SUCCESS,msg['success'])
            form = ViewerMessageForm()
        else:
            messages.add_message(request,messages.ERROR,msg['error'])
    context = {
        'settings':get_setting(request),
        'form':form,
        'categories':get_category(request),
    }
    return render(request,template_name,context)

def subscribe(request):
    try:
        validate_email(request.GET.get('email'))
        subscriber,crtd = Subscriber.objects.update_or_create(email=request.GET.get('email'))
        return JsonResponse({'status':'berhasil','pesan':'thanks for your subscription!'})
    except:
        return JsonResponse({'status':'gagal','pesan':'oops..something wrong, please try again.'})