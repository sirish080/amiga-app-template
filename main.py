# Copyright (c) farm-ng, inc.
#
# Licensed under the Amiga Development Kit License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://github.com/farm-ng/amiga-dev-kit/blob/main/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import uvicorn
from farm_ng.core.event_client_manager import (
    EventClient,
    EventClientSubscriptionManager,
)
from farm_ng.core.event_service_pb2 import EventServiceConfigList
from farm_ng.core.event_service_pb2 import SubscribeRequest
from farm_ng.core.events_file_reader import proto_from_json_file
from farm_ng.core.uri_pb2 import Uri
from fastapi import FastAPI
from fastapi import WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from google.protobuf.json_format import MessageToJson

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Initializing App...")
    asyncio.create_task(event_manager.update_subscriptions())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# to store the events clients
clients: dict[str, EventClient] = {}


@app.get("/list_uris")
async def list_uris() -> JSONResponse:
    """Return all the uris from the event manager."""
    all_uris_list: EventServiceConfigList = event_manager.get_all_uris_config_list(
        config_name="all_subscription_uris"
    )
    print(all_uris_list)
    return JSONResponse(content=json.loads(MessageToJson(all_uris_list)))


@app.websocket("/subscribe/{service_name}/{uri_path}")
async def subscribe(websocket: WebSocket, service_name: str, uri_path: str, every_n: int = 1):
    """Coroutine to subscribe to an event service via websocket.
    
    Args:
        websocket (WebSocket): the websocket connection
        service_name (str): the name of the event service
        uri_path (str): the uri path to subscribe to
        every_n (int, optional): the frequency to receive events. Defaults to 1.
    
    Usage:
        ws = new WebSocket("ws://localhost:8042/subscribe/oak0/left
    """

    client: EventClient = clients[service_name]

    await websocket.accept()

    async for _, message in client.subscribe(
        request=SubscribeRequest(uri=Uri(path=f"/{uri_path}"), every_n=every_n), decode=True
    ):
        await websocket.send_json(MessageToJson(message))

    await websocket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True, help="config file")
    parser.add_argument("--port", type=int, default=8042, help="port to run the server")
    parser.add_argument("--debug", action="store_true", help="debug mode")
    args = parser.parse_args()

    # NOTE: we only serve the react app in debug mode
    if not args.debug:
        react_build_directory = Path(__file__).parent / "ts" / "dist"

        app.mount(
            "/",
            StaticFiles(directory=str(react_build_directory.resolve()), html=True),
        )

    # config with all the configs
    base_config_list: EventServiceConfigList = proto_from_json_file(
        args.config, EventServiceConfigList()
    )

    # filter out services to pass to the events client manager
    service_config_list = EventServiceConfigList()
    for config in base_config_list.configs:
        if config.port == 0:
            continue
        service_config_list.configs.append(config)

    event_manager = EventClientSubscriptionManager(config_list=service_config_list)
    print(event_manager)

    # run the server
    uvicorn.run(app, host="0.0.0.0", port=args.port)  # noqa: S104
