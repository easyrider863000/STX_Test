from django.contrib import admin
from .models import *

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Bookauthor)
admin.site.register(Isbnnumber)
admin.site.register(Language)
