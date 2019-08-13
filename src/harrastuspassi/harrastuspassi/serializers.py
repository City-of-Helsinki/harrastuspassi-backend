from rest_framework import serializers
from harrastuspassi.models import Hobby, HobbyCategory, Location


class ExtraDataMixin():
    """ Mixin for serializers that provides conditionally included extra fields """
    INCLUDE_PARAMETER_NAME = 'include'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'context' in kwargs and 'request' in kwargs['context']:
            request = kwargs['context']['request']
            includes = request.GET.getlist(self.INCLUDE_PARAMETER_NAME)
            self.fields.update(self.get_extra_fields(includes, context=kwargs['context']))

    def get_extra_fields(self, includes, context):
        """ Return a dictionary of extra serializer fields.
        includes is a list of requested extra data.

        Example:
            fields = {}
            if 'user' in includes:
                fields['user'] = UserSerializer(read_only=True, context=context)
            return fields
        """
        return {}


class HobbyCategorySerializer(ExtraDataMixin, serializers.ModelSerializer):
    def get_extra_fields(self, includes, context):
        fields = super().get_extra_fields(includes, context)
        if 'child_categories' in includes:
            fields['child_categories'] = HobbyCategoryTreeSerializer(many=True, source='get_children', context=context)
        return fields

    class Meta:
        model = HobbyCategory
        fields = ['id', 'name', 'tree_id', 'level', 'parent']


class HobbyCategoryTreeSerializer(serializers.ModelSerializer):
    """ Serializer for an arbitrarily deep tree of categories """
    def get_fields(self):
        fields = super().get_fields()
        fields['child_categories'] = HobbyCategoryTreeSerializer(many=True, source='get_children')
        return fields

    class Meta:
        model = HobbyCategory
        fields = ['id', 'name', 'tree_id', 'level', 'parent']


class LocationSerializer(serializers.ModelSerializer):
    lat = serializers.SerializerMethodField
    lon = serializers.SerializerMethodField

    def get_lat(self, obj):
        return obj.lat

    def get_lon(self, obj):
        return obj.lon

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
