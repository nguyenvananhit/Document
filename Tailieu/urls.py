from django.urls import path
from .views import  *
from .views import  incoming_documents_view, add_incoming_document, edit_incoming_document,delete_incoming_document, search_incoming_documents

from django.contrib.auth.views import LogoutView

urlpatterns = [

    path('list/', display_data, name='display_data'),
    path('login/', login, name='login'),
    path('document/', document, name='document'),
  path('home/', home, name='home'),
#    out document 
    path('outgoing_documents/', outgoing_documents_view, name='outgoing_documents'),
      # URL để xem danh sách tài liệu đi


    # URL để thêm tài liệu đi
    path('outgoing_documents/add/', add_outgoing_document, name='add_outgoing_document'),

    # URL để chỉnh sửa tài liệu đi
    path('outgoing_documents/edit/<int:id>/', edit_outgoing_document, name='edit_outgoing_document'),

    # URL để xóa tài liệu đi
    path('outgoing_documents/delete/<int:id>/', delete_outgoing_document, name='delete_outgoing_document'),

    # URL để tìm kiếm tài liệu đi
    path('outgoing_documents/search/', search_outgoing_documents, name='search_outgoing_documents'),


    path('internal_documents/', internal_documents_view, name='internal_documents'),

    path('internal-documents/', list_internal_documents, name='list_internal_documents'),
    path('internal-documents/add/', add_internal_document, name='add_internal_document'),
    path('internal-documents/edit/<int:id>/', edit_internal_document, name='edit_internal_document'),
    path('internal-documents/delete/<int:id>/', delete_internal_document, name='delete_internal_document'),

    path('contracts/', contracts_view, name='contracts'),

    path('search_documents/', search_documents_view, name='search_documents'),
    path('view_documents/', view_documents_view, name='view_documents'),

    # Auth 
     path('logout/', logout, name='logout'),
     #incomming
    path('incoming_documents/', incoming_documents_view, name='incoming_documents'),
     path('incoming_documents/add/',add_incoming_document, name='add_incoming_document'),
    path('incoming_documents/edit/<int:id>/', edit_incoming_document, name='edit_incoming_document'),
    path('incoming_documents/delete/<int:id>/', delete_incoming_document, name='delete_incoming_document'),
    path('incoming_documents/search/', search_incoming_documents, name='search_incoming_documents'),

    # User 
      path('users/', list_users, name='list_users'),
    path('users/add/', add_user, name='add_user'),
    path('users/edit/<int:id>/', edit_user, name='edit_user'),
    path('users/delete/<int:id>/', delete_user, name='delete_user'),

    # Contracts 
    path('contracts/',list_contracts, name='list_contracts'),
    path('contracts/add/', add_contract, name='add_contract'),
    path('contracts/edit/<str:id>/', edit_contract, name='edit_contract'),
    path('contracts/delete/<str:id>/', delete_contract, name='delete_contract'),

    # Profle 
    path('profile/', profile, name='profile'),
    path('about/', about, name='about'),
  
] 
