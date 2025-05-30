import aiofiles, sys, asyncio
from datetime import datetime
from memory import memory

class Logger:
    @staticmethod
    async def app_log(title: str, message: str):
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        line = f"[{current_time}] {title} => {message}\n"
        memory.console_data["msg"] = line
        async with aiofiles.open("app.log", mode="a") as file:
            await file.write(line)
            
            
    @staticmethod
    async def console_live_feed():
        length = len(memory.console_data) + len(memory.console_data["msg"]) + 1
        sys.stdout.write(f"\033[{length}A")  # ANSI escape: move cursor up N lines
        # positions view
        print("Positions:")
        for k, v in memory.console_data.items():
            if k != "msg":
                print(f" {v}    ")
        
        # msg view
        print("Recent Messages:")
        for msg in memory.console_data["msg"]:
            print(f" {msg.strip()}")
            
    @staticmethod
    async def start_console_loop(interval_sec=1):
        try:
            while True:
                await Logger.console_live_feed()
                await asyncio.sleep(interval_sec)
                import random
                memory.update_console_data_msg(f" msg -{random.randint(1, 100)}")
                memory.console_data[random.choice([1,2,3,4,5,])] = f"[{random.choice("LONG", "SHORT")}] -> {random.randint(1, 100)}"
        except asyncio.CancelledError:
            print("Console feed stopped.")
        

    # Print updated data
        
print("")    
print("")    
print("")    
asyncio.run(Logger.start_console_loop(1))
