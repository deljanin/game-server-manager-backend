from django.contrib.auth.models import User
from rest_framework import serializers
from .models import GameServer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True }}

    # Serializer checks the fields in the Meta model ^^^, validate them and if they are valid passes them down
    def create(self, validated_data):
        # Once passed, we create the new user. ** splits up the kw args from a dictionary
        user = User.objects.create_user(**validated_data)
        return user

class GameServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameServer
        # Only include the fields you expect from the user
        fields = ["id", "server_name", "run_command", "server_files", "is_running", "created_at"]

        # These fields are handled by the backend, not the user
        read_only_fields = ["id", "created_at", "path"]

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.path = f"game_servers/{instance.server_name}"
        instance.save()
        return instance
        