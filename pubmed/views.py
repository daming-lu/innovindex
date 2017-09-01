# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count

from django.http import HttpResponse, JsonResponse

# Create your views here.

from .models import Category, Paper


def index(request):
    print 'index\n!\n'
    context = {'latest_question_list': 'haha'}
    return render(request, 'pubmed/index.html', context)


def get_data(request):
    data = {
        "haha": 168,
        "hao": 123,
    }
    return JsonResponse(data)


class ChartData(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        """
        Return a list of all users.
        """

        cat = [[],[]]

        for y in range(2012, 2017):
            for c in range(1, 3):
                cat[c-1].append(len(Paper.objects.filter(year=y, category_id=c)))

        top_source_cat1 = Paper.objects.filter(category_id=1).values('source').annotate(
            amt=Count('uid')).order_by('-amt')[:5]
        # import pdb;pdb.set_trace()
        cat1_top_5_pubs_labels = []
        cat1_top_5_pubs_amt = []

        for source in top_source_cat1:
            cat1_top_5_pubs_labels.append(source['source'])
            cat1_top_5_pubs_amt.append(source['amt'])

        cat2_top_5_pubs_labels = []
        cat2_top_5_pubs_amt = []

        top_source_cat2 = Paper.objects.filter(category_id=2).values('source').annotate(
            amt=Count('uid')).order_by('-amt')[:5]

        for source in top_source_cat2:
            cat2_top_5_pubs_labels.append(source['source'])
            cat2_top_5_pubs_amt.append(source['amt'])

        # import pdb;pdb.set_trace()

        years = ['2012', '2013', '2014', '2015', '2016']
        data = {
            'pic1_2_labels': years,
            'cat1_5_years': cat[0],
            'cat2_5_years': cat[1],

            'cat1_top_5_pubs_labels': cat1_top_5_pubs_labels,
            'cat1_top_5_pubs_counts': cat1_top_5_pubs_amt,

            'cat2_top_5_pubs_labels': cat2_top_5_pubs_labels,
            'cat2_top_5_pubs_counts': cat2_top_5_pubs_amt,
        }
        return Response(data)
