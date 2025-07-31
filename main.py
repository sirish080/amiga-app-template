# Copyright (c) farm-ng, inc.
#
# Licensed under the Amiga Development Kit License (the "License");
# https://github.com/farm-ng/amiga-dev-kit/blob/main/LICENSE

from __future__ import annotations

import argparse
import asyncio
import subprocess
import platform
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

def shutdown_linux():
    """Shuts down the Linux machine if the OS is Linux."""
    if platform.system() != "Linux":
        raise EnvironmentError("This shutdown function is only intended for Linux systems.")
    try:
        subprocess.run(["echo", "Shutdown command would be executed here."], check=True)  # For testing purpose
        #subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[Shutdown] Command failed: {e}")
    except Exception as e:
        print(f"[Shutdown] Unexpected error: {e}")
        
def reboot_linux():
    """Reboots the Linux machine."""
    if platform.system() != "Linux":
        raise EnvironmentError("This reboot function is only for Linux systems.")
    try:
        subprocess.run(["sudo", "reboot"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[Reboot] Command failed: {e}")
    except Exception as e:
        print(f"[Reboot] Unexpected error: {e}")
        

@app.on_event("startup")
async def startup_event():
    print("[Startup] Initializing App...")


# Enable CORS for all origins (customize in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[WebSocket] Client connected")

    try:
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                print(f"[WebSocket] Received: {msg}")

                action = msg.get("action")

                if action == "shutdown":
                    await websocket.send_json({"status": "shutting_down"})
                    shutdown_linux()
                elif action == "reboot":
                    await websocket.send_json({"status": "rebooting"})
                    reboot_linux()
                else:
                    await websocket.send_json({"error": f"unknown action '{action}'"})

            except asyncio.TimeoutError:
                pass  # No message this cycle

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected")
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True, help="config file")
    parser.add_argument("--port", type=int, default=8042, help="port to run the server")
    parser.add_argument("--debug", action="store_true", help="debug mode")
    args = parser.parse_args()

    if not args.debug:
        react_build_directory = Path(__file__).parent / "ts" / "dist"
        app.mount("/", StaticFiles(directory=str(react_build_directory.resolve()), html=True))

    uvicorn.run(app, host="0.0.0.0", port=args.port)
