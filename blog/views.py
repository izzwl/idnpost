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

def load_more(request):
    try:
        last_post = Post.objects.get(pk=request.GET.get('last_id')) 
    except:
        return JsonResponse({'data':None})
    try:
        category = Category.objects.get(pk=request.GET.get('category'))
        filter_category = Q(category=category)
    except:
        category = None
        filter_category = Q()

    active_post = Post.objects.select_related('writer','category',).prefetch_related('tags')\
        .filter(
            Q(is_active=True) and Q(dt_add__lt=last_post.dt_add) and filter_category
        ).order_by('-dt_add')[:5]
    post_list = []
    for ap in active_post:
        data = {
            'id':ap.id,
            'url':ap.url,
            'thumbnail__url':ap.thumbnail.url,
            'heading':ap.heading,
            'snippet':ap.snippet,
            'writer__first_name':ap.writer.first_name,
            'writer__last_name':ap.writer.last_name,
            'category__url':ap.category.url,
            'category__name':ap.category.name,
            'dt_add':ap.dt_add.strftime('%b %d, %Y'),
            'read_time':ap.read_time,
        }
        post_list.append(data)
    return JsonResponse({'data':post_list})

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
    
    if post:
        post.total_view += 1
        post.save()
         
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