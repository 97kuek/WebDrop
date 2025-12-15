from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

# 接続しているクライアントの管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = [] # 接続しているクライアントのリスト(WebSocket型)

    # 接続したときにリストに追加する
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Number of clients: {len(self.active_connections)}")

    # 切断したときにリストから除外する
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print("Client disconnected.")

    # 受け取ったメッセージを、自分以外の全員に送る（ブロードキャスト）
    async def broadcast(self, message: str, sender: WebSocket):
        for connection in self.active_connections:
            if connection != sender: # 自分には送り返さない
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # ブラウザからテキスト（SDPやICE Candidateなどの通信情報）を受け取る
            data = await websocket.receive_text()
            
            # 受け取った情報をそのまま他の人に転送する
            # ここでは中身を理解せず、ただ右から左へ流すのがポイント
            await manager.broadcast(data, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)