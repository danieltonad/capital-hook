from apscheduler.schedulers.asyncio import AsyncIOScheduler
from service.capital_socket import capital_socket
from service.capital_api import update_auth_header


class Jobs:
    
    async def run(self):
        scheduler = AsyncIOScheduler()
        
        # ping socket
        scheduler.add_job(capital_socket.ping_socket, "interval", minutes=5)
        # update auth header
        scheduler.add_job(update_auth_header, "interval", minutes=5)
        # start schd
        scheduler.start()
        for job in scheduler.get_jobs():
            print("Next Job: ", job.next_run_time)
            
            


jobs = Jobs()