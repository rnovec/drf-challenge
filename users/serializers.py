from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import User, Organization


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
        fields = ['id', 'name']


class UserDefaultSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = User
        exclude = []


class UserInfoSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'email',
                  'birthdate', 'organization']


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'email',
                  'birthdate', 'groups', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        org = validated_data['org']
        groups = validated_data['groups']
        user = User(name=validated_data['name'],
                    phone=validated_data['phone'],
                    email=validated_data['email'],
                    birthdate=validated_data['birthdate'],
        )
        user.organization = org
        user.set_password(validated_data['password'])
        user.save()
        user.groups.set(groups)
        return user
