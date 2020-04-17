from django.contrib import admin
from .models import Post,Category,Tag,ViewerMessage,Subscriber,Setting
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = (
        'url','writer','category','dt_add','total_view','is_picked','is_active','dt_expire',
    )
    fields = (
        'thumbnail','url','dt_expire','is_active','is_picked','category','categories','tags',
        'heading','snippet','content'
    )
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.writer = request.user
        obj.read_time = ( len(obj.content.split(' ')) + 1 ) // 250
        super().save_model(request, obj, form, change)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','url',)
    fields = ('url','name','thumbnail',)

class TagAdmin(admin.ModelAdmin):
    list_display = ('name','url',)
    fields = ('url','name',)

class SettingAdmin(admin.ModelAdmin):
    list_display = ('name','value',)
    fields = ('name','value',)
    readonly_fields = ('name',)
    def has_add_permission(self,request):
        return False
    def has_delete_permission(self,request,obj=None):
        return False

admin.site.register(Post,PostAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Tag,TagAdmin)
admin.site.register(Subscriber)
admin.site.register(ViewerMessage)
admin.site.register(Setting,SettingAdmin)