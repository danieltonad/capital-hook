from apscheduler.schedulers.asyncio import AsyncIOScheduler
from service.socket_manager import socket_manager, memory
from service.capital_api import update_auth_header, get_epic_hours, update_markets


class Jobs:
    
    async def update_epic_hours(self):
        for epic in socket_manager.get_all_subscribed_epics():
            memory.trading_hours[epic] = await get_epic_hours(epic)
        print(f"EPIC_HOURS_UPDATED => ", len(socket_manager.get_all_subscribed_epics()))

    async def run(self):
        scheduler = AsyncIOScheduler()
        
        # ping socket
        scheduler.add_job(socket_manager.ping_all, "interval", minutes=5)
        # update auth header
        scheduler.add_job(update_auth_header, "interval", minutes=5)
        # update markets
        scheduler.add_job(update_markets, "interval", hours=5)
        # update epic hours
        scheduler.add_job(self.update_epic_hours, "interval", hours=5)

        # start schd
        scheduler.start()
        for job in scheduler.get_jobs():
            print("Next Job: ", job.next_run_time)


    async def resume_trades(self):
        from database import get_positions, delete_position
        from service.capital_api import get_open_positions, memory
        from model import PositionsModel
        from resume_trade import ResumeTradeExecution
        import asyncio

        deal_ids = [pos['deal_id'] for pos in await get_open_positions()]
        
        positions: list[PositionsModel] = await get_positions()
            
        for position in positions:
            if position.id in deal_ids:
                resume_trade = ResumeTradeExecution(
                    epic=position.epic,
                    size=position.size,
                    deal_id=position.id,
                    entry_price=position.entry_price,
                    entry_date=position.entry_date,
                    trade_direction=position.direction,
                    profit_price=position.profit_price,
                    loss_price=position.loss_price,
                    hook_name=position.hook_name,
                    exit_criteria=position.exit_criteria,
                    trail_sl=position.trail_sl
                )
                print(f"Resuming {position.epic} {position.direction.value} trade on [{position.hook_name}]")
                asyncio.create_task(resume_trade.execute_trade())
                await asyncio.sleep(2) # slight delay to avoid overload
                memory.update_trading_view_hooked_trades(epic=position.epic, direction=position.direction, hook_name=position.hook_name)
            else:
                print(f"Position {position.id} no longer active. Deleting from DB.")
                await delete_position(position.id)

jobs = Jobs()