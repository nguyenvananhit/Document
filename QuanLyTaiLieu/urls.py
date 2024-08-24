from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Tailieu.urls')),
  
    path('list/', include('Tailieu.urls')),
    path('login/', include('Tailieu.urls')),
    path('document/', include('Tailieu.urls')),
    path('dashboard/', include('Tailieu.urls')),
    path('home/', include('Tailieu.urls')),
    path('incoming_documents/', include('Tailieu.urls')),
    path('incoming_documents/add/', include('Tailieu.urls')),
    path('incoming_documents/edit/<int:id>/',include('Tailieu.urls')),
    path('incoming_documents/delete/<int:id>/',include('Tailieu.urls')),
    path('incoming_documents/view/<int:id>/',include('Tailieu.urls')),
    path('incoming_documents/search/', include('Tailieu.urls')),
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
