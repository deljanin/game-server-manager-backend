from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from .managers import manager 

class ServerLogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        # Require authentication
        if not self.scope.get("user") or not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.server_id = int(self.scope["url_route"]["kwargs"]["server_id"])
        log_queue = manager.get_log_queue(self.server_id)
        if not log_queue:
            await self.close()
            return

        await self.accept()
        self.streaming = True

        async def send_logs():
            try:
                while self.streaming:
                    try:
                        line = await asyncio.wait_for(log_queue.get(), timeout=5)
                        await self.send(json.dumps({"log": line}))
                    except asyncio.TimeoutError:
                        continue
            except asyncio.CancelledError:
                pass
            except Exception as e:
                await self.send(json.dumps({"error": str(e)}))

        self.log_task = asyncio.create_task(send_logs())

    async def disconnect(self, code):
        self.streaming = False
        if hasattr(self, "log_task"):
            self.log_task.cancel()
            try:
                await self.log_task
            except asyncio.CancelledError:
                pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data.get("action") == "command":
                # Optionally, validate/limit commands here
                await manager.send_command(self.server_id, data["command"])
        except Exception as e:
            await self.send(json.dumps({"error": str(e)}))