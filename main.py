from fastapi import FastAPI, Form
from starlette.endpoints import WebSocketEndpoint, HTTPEndpoint
from starlette.responses import HTMLResponse
from starlette.routing import Route, WebSocketRoute, websocket_session
from database import info
from starlette.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn

templates = Jinja2Templates(directory='templates')
user_name = []


class Login(HTTPEndpoint):
    async def get(self, request: Request):
        return templates.TemplateResponse('login.html', {'request': request})


class Homepage(HTTPEndpoint):
    async def post(self, request: Request, username: str = Form(...)):
        print(username)
        user_name.append(username)
        print(username, '=='*50)
        return templates.TemplateResponse('index.html', {'request': request, 'username': username})


class Echo(WebSocketEndpoint):
    encoding = "text"

    async def alter_socket(self, websocket):
        socket_str = str(websocket)[1:-1]
        socket_list = socket_str.split(' ')
        socket_only = socket_list[3]
        return socket_only

    async def on_connect(self, websocket):
        await websocket.accept()
        socket_only = await self.alter_socket(websocket)
        info[socket_only] = [f'{user_name}', websocket]
        for wbs in info:
            await info[wbs][1].send_text(f"{info[socket_only][0]}-加入了聊天室")
        print(info)

    async def on_receive(self, websocket, data):
        socket_only = await self.alter_socket(websocket)
        for wbs in info:
            await info[wbs][1].send_text(f"{info[socket_only][0]}: {data}")

    async def on_disconnect(self, websocket, close_code):
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


routes = [
    Route("/", Login),
    Route("/chat/", Homepage),
    WebSocketRoute("/ws", Echo)
]

app = FastAPI(routes=routes)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
