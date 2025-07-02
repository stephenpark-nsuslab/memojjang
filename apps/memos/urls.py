from django.urls import path
from .views import MemoListView, MemoDetailView, MemoCreateView, MemoUpdateView, MemoDeleteView

urlpatterns = [
    path('', MemoListView.as_view(), name='memo-list'),
    path('<int:pk>/', MemoDetailView.as_view(), name='memo-detail'),
    path('new/', MemoCreateView.as_view(), name='memo-create'),
    path('<int:pk>/edit/', MemoUpdateView.as_view(), name='memo-update'),
    path('<int:pk>/delete/', MemoDeleteView.as_view(), name='memo-delete'),
]
