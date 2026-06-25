import os
import sys
import asyncio
import httpx
import socketio
import random
import string
import time
from rich.console import Console

console = Console()
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
WS_URL = os.getenv("WS_URL", "http://localhost:8000")

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def run_smoke_test():
    console.print("[bold cyan]Starting Holistic Interview Intelligence Smoke Test...[/bold cyan]")
    
    # 1. Check Health
    console.print("\n[yellow]1. Checking Health Endpoint...[/yellow]")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{API_URL}/health")
            resp.raise_for_status()
            console.print("[green]✓ Health check passed[/green]")
        except Exception as e:
            console.print(f"[red]✗ Health check failed: {e}[/red]")
            return False

    # 2. Register & Login
    console.print("\n[yellow]2. Registering and Logging in...[/yellow]")
    email = f"test_{random_string()}@example.com"
    password = "StrongPassword123!"
    token = None
    
    async with httpx.AsyncClient() as client:
        try:
            # Register
            reg_resp = await client.post(
                f"{API_URL}/auth/register",
                json={"email": email, "password": password, "full_name": "Smoke Test User"}
            )
            reg_resp.raise_for_status()
            
            # Login
            login_resp = await client.post(
                f"{API_URL}/auth/login",
                data={"username": email, "password": password}
            )
            login_resp.raise_for_status()
            token = login_resp.json()["access_token"]
            console.print("[green]✓ Authentication flow passed[/green]")
        except Exception as e:
            console.print(f"[red]✗ Auth flow failed: {e}[/red]")
            return False

    # 3. Create Interview
    console.print("\n[yellow]3. Creating an Interview Session...[/yellow]")
    interview_id = None
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            resp = await client.post(
                f"{API_URL}/interviews/sessions",
                headers=headers,
                json={"title": "Smoke Test Interview", "job_role": "Software Engineer", "difficulty": "medium"}
            )
            resp.raise_for_status()
            interview_id = resp.json().get("id")
            console.print(f"[green]✓ Interview created (ID: {interview_id})[/green]")
        except Exception as e:
            console.print(f"[red]✗ Interview creation failed: {e}[/red]")
            return False

    # 4. WebSocket Connection
    console.print("\n[yellow]4. Testing WebSocket Connection...[/yellow]")
    sio = socketio.AsyncClient()
    ws_connected = False
    
    @sio.event
    async def connect():
        nonlocal ws_connected
        ws_connected = True
        console.print("[green]✓ WebSocket connected[/green]")
        
    @sio.event
    async def disconnect():
        pass

    try:
        # Pass JWT token in headers or auth payload depending on backend implementation
        await sio.connect(
            WS_URL, 
            socketio_path='/ws/socket.io', 
            auth={"token": token},
            transports=['websocket']
        )
        await asyncio.sleep(2) # Give it time to connect and verify
        if not ws_connected:
            raise Exception("Did not receive connect event")
        await sio.disconnect()
    except Exception as e:
        console.print(f"[red]✗ WebSocket test failed: {e}[/red]")
        return False

    console.print("\n[bold green]🎉 ALL SMOKE TESTS PASSED![/bold green]")
    return True

if __name__ == "__main__":
    success = asyncio.run(run_smoke_test())
    sys.exit(0 if success else 1)
