import os
import shutil
from django.db import models
from django.contrib.auth.models import User

class GameServer(models.Model):
    server_name = models.CharField(max_length=100)
    is_running = models.BooleanField(default=False)
    path = models.CharField(max_length=256)
    run_command = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    server_files = models.FileField(upload_to='game_servers/')

    def __str__(self):
        return self.server_name

    def delete(self, *args, **kwargs):
        # Remove the extracted server directory
        if self.path and os.path.isdir(self.path):
            shutil.rmtree(self.path)
        super().delete(*args, **kwargs)