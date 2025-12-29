from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Dict
import socket
import os

app = FastAPI()

# テンプレートエンジン (Jinja2) の設定
templates = Jinja2Templates(directory=".")



def get_local_ip():
    """自身のローカルIPアドレスを取得する"""
    try:
        # UDPソケットを使って接続先を解決させる（実際には接続しない）
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def print_all_ips():
    print("\n--- Available Network Interfaces ---")
    try:
        hostname = socket.gethostname()
        print(f"Hostname: {hostname}")
        for ip in socket.gethostbyname_ex(hostname)[2]:
            print(f" -> {ip}")
    except Exception as e:
        print(f"Error listing IPs: {e}")
    print("------------------------------------\n")

# 起動時に全IPを表示（デバッグ用）
print_all_ips()

# 部屋ごとの接続を管理するクラス
class ConnectionManager:
    def __init__(self):
        self.active_rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = []
        self.active_rooms[room_id].append(websocket)
        print(f"Client joined room: {room_id}. Total members: {len(self.active_rooms[room_id])}")

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_rooms:
            if websocket in self.active_rooms[room_id]:
                self.active_rooms[room_id].remove(websocket)
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]
        print(f"Client left room: {room_id}")

    async def broadcast(self, message: str, sender: WebSocket, room_id: str):
        if room_id in self.active_rooms:
            for connection in self.active_rooms[room_id]:
                if connection != sender:
                    await connection.send_text(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    # アクセス時にIPアドレスを検出し、テンプレートに渡す
    host_ip = get_local_ip()
    return templates.TemplateResponse("index.html", {"request": request, "host_ip": host_ip})

@app.get("/manifest.json")
async def get_manifest():
    return FileResponse("manifest.json")

@app.get("/icon.svg")
async def get_icon():
    return FileResponse("icon.svg")

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data, websocket, room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)