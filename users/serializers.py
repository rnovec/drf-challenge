from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import User, Organization
from .constants import USER_INFO_FIELDS, ORG_INFO_FIELDS, USER_CREATE_FIELDS

class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='codename'
    )

    class Meta:
        model = Group
        exclude = []


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ORG_INFO_FIELDS


class OrganizationRelatedField(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name']


class UserOrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']


class UserDefaultSerializer(serializers.ModelSerializer):
    organization = OrganizationRelatedField(read_only=True)

    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = User
        exclude = []


class UserInfoSerializer(serializers.ModelSerializer):
    organization = OrganizationRelatedField(read_only=True)

    class Meta:
        model = User
        fields = USER_INFO_FIELDS


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = USER_CREATE_FIELDS
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(name=validated_data.get('name'),
                    phone=validated_data.get('phone'),
                    email=validated_data.get('email'),
                    birthdate=validated_data.get('birthdate'))
        user.organization = validated_data.get('org')
        user.set_password(validated_data.get('password'))
        user.save()

        groups = validated_data.get('groups', [])
        user.groups.set(groups)
        return user
