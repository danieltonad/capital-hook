from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title=""
)



app.mount("/assets", StaticFiles(directory="assets"), name="assets")