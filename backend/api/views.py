import zipfile, os
from rest_framework import viewsets
from rest_framework.decorators import action
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, GameServerSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import GameServer
from .managers import manager
from asgiref.sync import async_to_sync


class GameServerViewSet(viewsets.ModelViewSet):
    queryset = GameServer.objects.all()
    serializer_class = GameServerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        zip_file = instance.server_files

        server_folder = os.path.join(settings.SERVERS_DIR, instance.server_name)
        print(f"Creating server folder at: {server_folder}")
        os.makedirs(server_folder, exist_ok=True)

        # Stream the uploaded file to a temp file to avoid memory issues
        temp_zip_path = os.path.join(server_folder, f"{instance.server_name}.zip")
        print(f"Saving uploaded zip to: {temp_zip_path}")
        total_written = 0
        with open(temp_zip_path, 'wb+') as destination:
            for chunk in zip_file.chunks():
                destination.write(chunk)
                total_written += len(chunk)

        print("Finished writing zip file, now inspecting contents...")

        # Inspect the zip file to check for a single root directory
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            names = zip_ref.namelist()
            # Remove trailing slashes and get top-level folders/files
            top_levels = set([name.split('/')[0] for name in names if name.strip()])

            if len(top_levels) == 1:
                # Only one root directory, extract its contents directly into server_folder
                root_dir = list(top_levels)[0]
                print(f"Single root directory '{root_dir}' found, extracting its contents into {server_folder}")
                for member in zip_ref.infolist():
                    member_path = member.filename
                    # Remove the root_dir prefix
                    if member_path.startswith(root_dir):
                        relative_path = member_path[len(root_dir):].lstrip('/')
                        target_path = os.path.join(server_folder, relative_path)
                        if member.is_dir():
                            os.makedirs(target_path, exist_ok=True)
                        else:
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            with zip_ref.open(member) as source, open(target_path, "wb") as target:
                                target.write(source.read())
            else:
                print("Multiple top-level items, extracting as-is.")
                zip_ref.extractall(server_folder)

        print("Extraction complete.")

        # Remove the uploaded ZIP file after extraction
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)
            print(f"Removed temp zip file: {temp_zip_path}")

        # Set the server path to server_folder (since contents are now directly inside)
        instance.path = server_folder
        instance.save()
        print("perform_create finished and instance saved.")

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        server = self.get_object()
        if manager.is_running(server.id):
            return Response({'detail': 'Server already running.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            print(f"Starting server {server.id} with command: '{server.run_command}' in '{server.path}'")
            async_to_sync(manager.start_server)(server.id, server.run_command.split(), server.path)
            server.is_running = True
            server.save(update_fields=['is_running'])
            return Response({'status': 'started'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        server = self.get_object()
        if not manager.is_running(server.id):
            return Response({'detail': 'Server not running.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            async_to_sync(manager.stop_server)(server.id)
            server.is_running = False
            server.save(update_fields=['is_running'])
            return Response({'status': 'stopped'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
