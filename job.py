from apscheduler.schedulers.asyncio import AsyncIOScheduler
from service.capital_socket import capital_socket


class Jobs:
    
    async def run(self):
        scheduler = AsyncIOScheduler()
        
        scheduler.add_job(capital_socket.ping_socket, "interval", minutes=5)
        # start schd
        scheduler.start()
        for job in scheduler.get_jobs():
            print("Next Job: ", job.next_run_time)