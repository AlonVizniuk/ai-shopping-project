from fastapi import FastAPI
from config.database import database
from controller.user_controller import router as user_router
from controller.auth_controller import router as auth_router
from controller.item_controller import router as item_router
from controller.favorite_controller import router as favorite_router
from controller.order_controller import router as order_router
from controller.chat_controller import router as chat_router

app = FastAPI()


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(item_router)
app.include_router(favorite_router)
app.include_router(order_router)
app.include_router(chat_router)

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def health_check():
    return {"message": "AI Shopping backend is running"}