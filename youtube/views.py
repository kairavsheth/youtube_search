# Create your views here.

import googleapiclient.discovery
import googleapiclient.errors
from django.contrib.postgres.search import TrigramSimilarity
from django.db import IntegrityError
from django.db.models.functions import Greatest
from rest_framework import generics, filters
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from youtube.models import Video
from youtube.serializers import VideoSerializer
from youtube_search.settings import YT_API_KEY


class TrigramSimilaritySearchFilter(SearchFilter):
    search_param = api_settings.SEARCH_PARAM
    template = 'rest_framework/filters/search.html'
    search_title = 'Search'
    search_description = 'A search term.'

    def get_trigram_similarity(self, view, request):
        return getattr(view, 'trigram_similarity', 0.3)

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, '')
        params = params.replace('\x00', '')  # strip null characters
        params = params.replace(',', ' ')
        return params.split()

    def get_search_fields(self, view, request):
        """
        Search fields are obtained from the view, but the request is always
        passed to this method. Sub-classes can override this method to
        dynamically change the search fields based on request content.
        """
        return getattr(view, 'search_fields', None)

    def filter_queryset(self, request, queryset, view):
        trigram_similarity = self.get_trigram_similarity(view, request)
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        # if no search_terms return
        if not search_terms:
            return queryset

        # make conditions
        conditions = []
        for search_term in search_terms:
            conditions.extend([
                TrigramSimilarity(field, search_term) for field in search_fields
            ])

        # take the greatest similarity from all conditions
        # and annotate as similarity
        return queryset.annotate(
            similarity=Greatest(*conditions)
        ).filter(similarity__gte=trigram_similarity)


class Fetch(APIView):
    def get(self, request):
        keyword = request.query_params.get('q', 'Apple')

        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YT_API_KEY)

        request = youtube.search().list(
            part="snippet",
            maxResults=50,
            q=keyword
        )
        response = list(filter(lambda x: x['id']['kind'] == 'youtube#video',
                          request.execute()[
                              'items']))  # improvise to fetch only videos using api instead of filterining over here
        duplicates = 0
        for i in response:
            try:
                Video(title=i['snippet']['title'], description=i['snippet']['description'],
                      video_id=i['id']['videoId']).save()
            except IntegrityError:
                duplicates += 1
        return Response(data={'message': 'Fetched', 'count': {'fetched': len(response), 'duplicates': duplicates,
                                                              'inserted': len(response) - duplicates}})


class List(generics.ListAPIView):
    serializer_class = VideoSerializer
    queryset = Video.objects.all()
    filter_backends = [filters.SearchFilter]
    # filter_backends = [TrigramSimilaritySearchFilter]
    search_fields = ['title', 'description']
