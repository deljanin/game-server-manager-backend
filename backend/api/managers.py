import asyncio

class GameServerManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameServerManager, cls).__new__(cls)
            cls._instance.servers = {}
        return cls._instance

    def __init__(self):
        self.servers = {}  # {server_id: {process, log_queue, stdout_task}}

    async def start_server(self, server_id, command, cwd):
        if server_id in self.servers:
            return f"{server_id} already running"

        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd  # Use the server's path as working directory
        )

        log_queue = asyncio.Queue(maxsize=1000)

        # Task to continuously read logs, put them into a queue and pop old logs if the queue is full
        async def read_stdout():
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                decoded_line = line.decode()
                # print(f"[Server {server_id} LOG]: {decoded_line.strip()}")  # <-- Print game server logs to console
                await self._enqueue_log(log_queue, decoded_line)

        task = asyncio.create_task(read_stdout())


        self.servers[server_id] = {
            "process": process,
            "log_queue": log_queue,
            "stdout_task": task
        }
        return f"{server_id} started"

    async def stop_server(self, server_id):
        if server_id not in self.servers:
            return f"{server_id} not running"

        process = self.servers[server_id]["process"]
        process.terminate()
        await process.wait()
        del self.servers[server_id]
        return f"{server_id} stopped"

    async def send_command(self, server_id, command):
        if server_id not in self.servers:
            return f"{server_id} not running"

        process = self.servers[server_id]["process"]
        process.stdin.write((command + "\n").encode())
        await process.stdin.drain()
        return f"Sent: {command}"

    def get_log_queue(self, server_id):
        return self.servers.get(server_id, {}).get("log_queue")

    async def _enqueue_log(self, log_queue, line):
        try:
            log_queue.put_nowait(line)
        except asyncio.QueueFull:
            try:
                await log_queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            await log_queue.put(line)
    
    def is_running(self, server_id):
        return server_id in self.servers

manager = GameServerManager()