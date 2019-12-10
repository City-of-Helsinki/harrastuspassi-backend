from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from harrastuspassi.models import (
    Benefit,
    Hobby,
    HobbyCategory,
    HobbyEvent,
    Location,
    Organizer,
    Promotion,
)


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


class LocationSerializerPre1(serializers.ModelSerializer):
    lat = serializers.SerializerMethodField
    lon = serializers.SerializerMethodField

    def get_lat(self, obj):
        return obj.lat

    def get_lon(self, obj):
        return obj.lon

    class Meta:
        model = Location
        fields = ['id', 'name', 'address', 'zip_code', 'city', 'lat', 'lon']

class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ['id', 'name', 'address', 'zip_code', 'city', 'coordinates']


class OrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizer
        fields = ['id', 'name']


class HobbySerializer(ExtraDataMixin, serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    cover_image = Base64ImageField(required=False, allow_null=True)

    def get_extra_fields(self, includes, context):
        fields = super().get_extra_fields(includes, context)
        if 'location_detail' in includes:
            fields['location'] = LocationSerializer(read_only=True, context=context)
        if 'organizer_detail' in includes:
            fields['organizer'] = OrganizerSerializer(read_only=True, context=context)
        return fields

    def get_permissions(self, instance):
        if 'prefetched_permission_checker' in self.context:
            checker = self.context['prefetched_permission_checker']
            return {
                'can_edit': checker.has_perm('change_hobby', instance)
            }
        return {}

    class Meta:
        model = Hobby
        fields = [
            'categories',
            'cover_image',
            'description',
            'id',
            'location',
            'name',
            'organizer',
            'permissions',
        ]


class HobbySerializerPre1(HobbySerializer):
    category = serializers.SerializerMethodField()

    def get_category(self, instance):
        category = instance.categories.first()
        if category:
            return category.pk
        else:
            return None

    class Meta(HobbySerializer.Meta):
        fields = [
            'category',
            'cover_image',
            'description',
            'id',
            'location',
            'name',
            'organizer',
            'permissions',
        ]


class HobbyDetailSerializer(HobbySerializer):

    class Meta:
        model = Hobby
        fields = '__all__'


class HobbyDetailSerializerPre1(HobbySerializerPre1):
    organizer = serializers.StringRelatedField()

    class Meta:
        model = Hobby
        fields = '__all__'


class HobbyNestedSerializer(HobbySerializer):
    """ HobbySerializer providing related fields as nested data.
    Except category.
    TODO: category should also be nested.
    """
    location = LocationSerializer(read_only=True)
    organizer = OrganizerSerializer(read_only=True)

    class Meta(HobbySerializer.Meta):
        pass


class HobbyNestedSerializerPre1(HobbySerializerPre1):

    class Meta(HobbySerializerPre1.Meta):
        pass


class HobbyEventSerializer(ExtraDataMixin, serializers.ModelSerializer):
    def get_extra_fields(self, includes, context):
        fields = super().get_extra_fields(includes, context)
        if 'hobby_detail' in includes:
            fields['hobby'] = HobbyNestedSerializer(context=context)
        # TODO: DEPRECATE VERSION pre1
        request = context.get('request')
        if 'hobby_detail' in includes and request and request.version == 'pre1':
            fields['hobby'] = HobbyNestedSerializerPre1(context=context)
        return fields

    class Meta:
        model = HobbyEvent
        fields = ('end_date', 'end_time', 'hobby', 'id', 'start_date', 'start_time', 'start_weekday')
        read_only_fields = ('start_weekday',)


class PromotionSerializer(ExtraDataMixin, serializers.ModelSerializer):
    cover_image = Base64ImageField(required=False, allow_null=True)

    def get_extra_fields(self, includes, context):
        fields = super().get_extra_fields(includes, context)
        if 'location_detail' in includes:
            fields['location'] = LocationSerializer(read_only=True, context=context)
        if 'organizer_detail' in includes:
            fields['organizer'] = OrganizerSerializer(read_only=True, context=context)
        return fields

    class Meta:
        model = Promotion
        fields = '__all__'


class BenefitSerializer(serializers.ModelSerializer):

    def validate(self, data):
        promotion = data['promotion']
        promotion = Promotion.objects.get(pk=promotion.pk)
        if promotion.used_count >= promotion.available_count:
            raise serializers.ValidationError('All available promotions have been used')
        return data

    class Meta:
        model = Benefit
        fields = '__all__'