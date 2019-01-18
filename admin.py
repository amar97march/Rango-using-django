from rango.models import UserProfile

# Register your models here.
from django.contrib import admin
from rango.models import Category, Page

class categoryAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['name']}),
                 ('Others Info',{'fields': ['views','likes','slug']}),
                 ]
    prepopulated_fields = {'slug':('name',)}

admin.site.register(Category, categoryAdmin)
admin.site.register(Page)
admin.site.register(UserProfile)
