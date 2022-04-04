from django.contrib import admin
from django.urls import path
from bookapp import views
from bookapp import api_views

urlpatterns = [
    path('', views.index),
    path('import/', views.importBook),
    path('search/', views.searchBook),
    path('add-books-from-import/', views.addBooksFromImport),
    path('add-new-book/', views.addNewBook),
    path('delete-book/', views.deleteBook),
    path('edit-book/', views.editBook),
    path('admin/', admin.site.urls),
    path('api/search/', api_views.search)
]
