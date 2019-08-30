
# -*- coding: utf-8 -*-

from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView as BaseTokenObtainPairView


def get_harrastuspassi_token(user):
    token = RefreshToken.for_user(user)
    token['first_name'] = user.first_name
    token['last_name'] = user.last_name
    return token


class TokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        return get_harrastuspassi_token(user)


class TokenObtainPairView(BaseTokenObtainPairView):
    """ View for obtaining a pair of refresh and access tokens for API authentication.
        Response will contain both:
            {
                "access":"<access token>",
                "refresh":"<refresh token>"
            }

        The access token must be included as a header in subsequent API calls:
            Authorization: Bearer <access token>
    """
    authentication_classes = [SessionAuthentication]
    serializer_class = TokenPairSerializer

    def get(self, request, *args, **kwargs):
        # User with valid session authentication can receive tokens via simple GET
        if request.user.is_authenticated:
            refresh_token = get_harrastuspassi_token(request.user)

            data = {
                'refresh': str(refresh_token),
                'access': str(refresh_token.access_token),
            }
            return Response(data)
        else:
            raise NotAuthenticated
