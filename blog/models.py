import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils.deconstruct import deconstructible
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.core.validators import RegexValidator
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField


phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message=_("Phone number must be entered in the format: '+99999999' up to 15 digits allowed")
)
@deconstructible
class UploadImage(object):
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        try:
            dt = instance.dt_add
        except:
            dt = None
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(instance.url, ext)
        if dt:
            return os.path.join(self.sub_path, str(dt.year), str(dt.month), filename)
        else:
            return os.path.join(self.sub_path, filename)

upload_thumbnail = UploadImage('post-images/')
upload_category = UploadImage('category-images/')

# Create your models here.
class Page(models.Model):
    name = models.CharField(max_length=255)

class Category(models.Model):
    url = models.SlugField(unique=True,blank=True)
    name = models.CharField(max_length=25)
    thumbnail = models.ImageField(upload_to=upload_category, height_field='thumbnail_height', width_field='thumbnail_width', blank=True)
    thumbnail_width = models.PositiveIntegerField(default=0)
    thumbnail_height = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.name
    def save(self,*args,**kwargs):
        if not self.url:
            self.url = slugify(self.name)
        super().save(*args,**kwargs)
    class Meta:
        verbose_name_plural = 'Categories'     

class Tag(models.Model):
    url = models.SlugField(unique=True,blank=True)
    name = models.CharField(max_length=25)
    def __str__(self):
        return self.name
    def save(self,*args,**kwargs):
        if not self.url:
            self.url = slugify(self.name)
        super().save(*args,**kwargs)
class Post(models.Model):
    url = models.SlugField(unique=True,blank=True)
    writer = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,verbose_name=_('Writer'))
    read_time = models.PositiveIntegerField(_('Read Time Estimation'))
    total_view = models.PositiveIntegerField(_('Total Read'),default=0)
    dt_add = models.DateTimeField(_('Date Add'),auto_now_add=True)
    dt_expire = models.DateTimeField(_('Date Expire'),null=True,default=None,blank=True)
    is_active = models.BooleanField(_('Active'),default=False)
    is_picked = models.BooleanField(_('Editor Pick'),default=False)
    category = models.ForeignKey(Category,on_delete=models.PROTECT,verbose_name=_('Category'))
    categories = models.ManyToManyField(Category,verbose_name=_('Other Category'),related_name='categories')
    tags = models.ManyToManyField(Tag,verbose_name=_('Tags'))
    heading = models.CharField(_('Heading'),max_length=255)
    source = models.CharField(_('Source'),max_length=255,blank=True)
    snippet = models.TextField(_('Snippet'))
    content = RichTextUploadingField(_('Content'))
    thumbnail = models.ImageField(upload_to=upload_thumbnail, height_field='thumbnail_height', width_field='thumbnail_width')
    thumbnail_width = models.PositiveIntegerField(default=0)
    thumbnail_height = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.heading
    def save(self,*args,**kwargs):
        if not self.url:
            self.url = slugify(self.heading) 
        super().save(*args,**kwargs)

class PostRating(models.Model):
    dt_add = models.DateTimeField(_('Date Expire'),auto_now_add=True)
    viewer = models.ForeignKey(User,on_delete=models.SET_NULL,verbose_name=_('Viewer'),null=True,default=None)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    rate = models.PositiveIntegerField(_('Total Read'))

class ViewerMessage(models.Model):
    first_name = models.CharField(_('First Name'),max_length=20)
    last_name = models.CharField(_('Last Name'),max_length=20,blank=True)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Phone'),blank=True,validators=[phone_regex],max_length=16)
    message = models.TextField(_('Message'))
    def __str__(self):
        return self.email

class Subscriber(models.Model):    
    email = models.EmailField(_('Email'))
    def __str__(self):
        return self.email

class Setting(models.Model):
    name = models.CharField(_('Name'),max_length=25)
    value = models.CharField(_('Value'),max_length=255)
    def __str__(self):
        return self.name

@receiver(models.signals.post_delete, sender=Post)
def auto_delete_post_image_on_delete(sender, instance, **kwargs):
    f = 'thumbnail'
    try:
        file_ = getattr(instance,f)
        if file_:
            if os.path.isfile(file_.path):
                os.remove(file_.path)
    except:
        pass

@receiver(models.signals.pre_save, sender=Post)
def auto_delete_post_image_on_change(sender, instance, **kwargs):
    f = 'thumbnail'
    if not instance.pk:
        return False

    old_file = None
    try:
        oldinst = sender.objects.get(pk=instance.pk)
        old_file = getattr(oldinst,f)
    except:
        pass
    try:    
        new_file = getattr(instance,f)
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except:
        pass