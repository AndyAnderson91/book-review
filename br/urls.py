from django.urls import path
from . import views

app_name = 'br'
urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),
    path('recent/', views.RecentListView.as_view(), name='recent'),
    path('popular/', views.PopularListView.as_view(), name='popular'),
    path('ratings/', views.RatingTemplateView.as_view(), name='ratings'),
    path('search/', views.SearchTemplateView.as_view(), name='search'),
]
