from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^api/data$', views.get_data),
    url(r'^pubmed/api/chart/data$', views.ChartData.as_view()),
]
