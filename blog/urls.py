from django.urls import path
from .views import (PostListView,
                    PostDetailView,
                    PostCreateView,
                    PostUpdateView,
                    PostDeleteView,
                    PostStatistics,
                    page_not_found,
                    bad_request,
                    GeneratePDF,
                    GetMail)

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('statistics', PostStatistics.as_view(), name='statistics'),
    path('pdf-download', GeneratePDF.as_view(), name='pdf-download'),
    path('get-mail', GetMail.as_view(), name='receive-email'),
    path('404', page_not_found, name='page-not-found'),
    path('400', bad_request, name='not-efficient-tag')
]
