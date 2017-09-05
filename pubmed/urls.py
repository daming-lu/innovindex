from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^api/data$', views.get_data, name='next_page'),
    url(r'^team$', views.get_team, name='get_team'),
    url(r'^pubmed/api/chart/data$', views.ChartData.as_view(), name='show_chart')
]
