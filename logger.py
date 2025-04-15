import aiofiles
from datetime import datetime

class Logger:
    @staticmethod
    async def app_log(title: str, message: str):
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        line = f"[{current_time}] {title} => {message}\n"
        print(line)
        async with aiofiles.open("app.log", mode="a") as file:
            await file.write(line)