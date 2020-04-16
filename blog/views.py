from django.shortcuts import render
from django.db.models import Q
from django.http import Http404,HttpResponse
from .models import Post,Category,Tag
# Create your views here.
def get_category(request):
    filter = {
        'is_active':True,
    }
    order = ['pk',]
    categories = Category.objects.all().order_by(*order)
    return categories

def home(request,template_name='web/home.html'):
    active_post = Post.objects.select_related('writer','category',).prefetch_related('tags').filter(is_active=True)
    context = {
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
        'category':category,
        'post':post,
        'categories':get_category(request),
        'related_posts':active_post.order_by('-total_view')[:5],
    }
    return render(request,template_name,context)