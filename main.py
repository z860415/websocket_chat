from fastapi import FastAPI, Form, WebSocket
from database import info
from starlette.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn

templates = Jinja2Templates(directory='templates')
user_name = []

app = FastAPI()


@app.get('/')
async def get(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})


@app.post('/chat/')
async def post(request: Request, username: str = Form(...)):
    user_name.append(username)
    return templates.TemplateResponse('index.html', {'request': request})


class Echo:
    async def alter_socket(self, websocket):
        socket_str = str(websocket)[1:-1]
        socket_list = socket_str.split(' ')
        socket_only = socket_list[3]
        return socket_only

    async def on_connect(self, websocket):
        await websocket.accept()
        socket_only = await self.alter_socket(websocket)
        info[socket_only] = [f'{user_name[-1]}', websocket]
        for wbs in info:
            await info[wbs][1].send_text(f"{info[socket_only][0]}-加入了聊天室")
        print(info)

    async def on_receive(self, websocket, data):
        socket_only = await self.alter_socket(websocket)
        for wbs in info:
            await info[wbs][1].send_text(f"{info[socket_only][0]}: {data}")

    async def on_disconnect(self, websocket):
        socket_only = await self.alter_socket(websocket)
        socket_name = info[socket_only][0]
        for wbs in info:
            try:
                await info[wbs][1].send_text(f"{socket_name}-離開了聊天室")
            except:
                continue
        info.pop(socket_only)
        print(info)
        pass


manager = Echo()


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await manager.on_connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.on_receive(websocket, data)
    except:
        await manager.on_disconnect(websocket)


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
