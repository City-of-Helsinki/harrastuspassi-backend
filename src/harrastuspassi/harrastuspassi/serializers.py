from rest_framework import serializers
from harrastuspassi.models import Hobby, HobbyCategory, Location


class HobbyCategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = HobbyCategory
    fields = ['id', 'name', 'tree_id', 'level', 'parent']


class LocationSerializer(serializers.ModelSerializer):
  lat = serializers.SerializerMethodField
  lon = serializers.SerializerMethodField

  def get_lat(self, obj):
    return obj.lat()

  def get_lon(self, obj):
    return obj.lon()

  class Meta:
    model = Location
    fields = ['id', 'name', 'address', 'zip_code', 'city', 'lat', 'lon']


class HobbySerializer(serializers.ModelSerializer):
  location = LocationSerializer()
  start_day_of_week = serializers.CharField(source='get_start_day_of_week_display')
  end_day_of_week = serializers.CharField(source='get_end_day_of_week_display')


  class Meta:
    model = Hobby
    fields = [
      'id',
      'name',
      'start_day_of_week',
      'end_day_of_week',
      'location',
      'cover_image',
      'category',
    ]

class HobbyDetailSerializer(HobbySerializer):
  organizer = serializers.StringRelatedField()

  class Meta:
    model = Hobby
    fields = '__all__'
