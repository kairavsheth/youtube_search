from rest_framework import serializers

from youtube.models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        exclude = ['id']
