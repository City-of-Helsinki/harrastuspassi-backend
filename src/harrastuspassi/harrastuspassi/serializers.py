from rest_framework import serializers
from harrastuspassi.models import Hobby


class HobbySerializer(serializers.ModelSerializer):
  location = serializers.CharField(source='name')
  day_of_week = serializers.CharField(source='get_day_of_week_display')

  class Meta:
    model = Hobby
    fields = ['name', 'day_of_week', 'location', 'image']
