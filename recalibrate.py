import time

class TrailRecalibration:
    def __init__(self, profit_percentage: float, trail: float, recal_cooldown_sec: float = 60.0, min_recal_pnl : float = 100.0):
        self.profit_percentage = profit_percentage
        self.trail = trail
        self.recal_cooldown_sec = recal_cooldown_sec
        self.min_recal_pnl = min_recal_pnl

        self.is_active = False
        self.in_recalibration = False
        self._recal_start_time = None
        
        self.new_max = 0.0
        self.cutoff = None
        self.last_pnl = 0.0

    def pnl_percentage_ratio(self, profit: float, loss: float) -> tuple[float, float]:
        abs_p = abs(profit)
        abs_l = abs(loss)
        total = abs_p + abs_l
        if total == 0:
            return (0.0, 0.0)
        return (round((abs_p / total) * 100, 2), round((abs_l / total) * 100, 2))

    def update_pnl(self, gross_profit: float, gross_loss: float, current_time: float = None) -> bool:
        if current_time is None:
            current_time = time.time()

        net_pnl = gross_profit - gross_loss
        self.last_pnl = net_pnl
        profit_pct, _ = self.pnl_percentage_ratio(gross_profit, gross_loss)

        # 🔹 Auto-exit recalibration after cooldown
        if self.in_recalibration and self._recal_start_time:
            if current_time - self._recal_start_time >= self.recal_cooldown_sec:
                self.exit_recalibration()
                # After exit, don't return True anymore
                return False
            else:
                # Still in cooldown → keep returning True!
                return True

        # 🔹 If we're here, NOT in recalibration
        # Check activation
        if not self.is_active:
            if self.profit_percentage and profit_pct >= self.profit_percentage:
                self._activate_trailing(net_pnl)

        # 🔹 Trailing monitoring
        if self.is_active:
            if net_pnl > self.new_max:
                self.new_max = net_pnl
                self.cutoff = self.new_max * (1 - self.trail / 100.0)
            elif ( self.cutoff is not None and net_pnl >= self.min_recal_pnl  and net_pnl <= self.cutoff):
                # Trigger recalibration → will return True from now on (for 60 sec)
                self.recalibrate(current_time)
                return True  # return True immediately

        return False

    def _activate_trailing(self, pnl: float):
        self.is_active = True
        self.new_max = pnl
        self.cutoff = self.new_max * (1 - self.trail / 100.0)

    def recalibrate(self, current_time: float):
        self.is_active = False
        self.in_recalibration = True
        self._recal_start_time = current_time
        self.new_max = self.last_pnl
        self.cutoff = None

    def exit_recalibration(self):
        self.in_recalibration = False
        self._recal_start_time = None

    def recalibration_status(self) -> dict:
        elapsed = time.time() - self._recal_start_time if self._recal_start_time else None
        return {
            "is_active": self.is_active,
            "in_recalibration": self.in_recalibration,
            "elapsed_sec": elapsed,
            "cutoff": self.cutoff
        }