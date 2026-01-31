class TrailingSL:
    def __init__(self, pnl: float, tp: float, sl: float, trail_range: float):
        self.pnl = pnl
        self.tp = tp
        self.sl = sl
        self.trail_range = trail_range

        self.trailing_active = False
        self.new_max = pnl
        self.cutoff = 0  # trailing stop, only meaningful when trailing_active

    def update_pnl(self, pnl: float) -> bool:
        self.pnl = pnl

        # Update new max PnL
        if pnl > self.new_max:
            self.new_max = pnl

        # Activate trailing if PnL exceeds 2 * trail_range
        if not self.trailing_active and pnl >= 2 * self.trail_range:
            self.trailing_active = True
            self.cutoff = self.new_max - self.trail_range

        # Update trailing stop if active
        if self.trailing_active:
            self.cutoff = max(self.cutoff, self.new_max - self.trail_range)

        # Determine active stop
        active_stop = self.cutoff if self.trailing_active else -float('inf')  # no stop before trailing

        # Check TP
        if pnl >= self.tp:
            return True

        # Check if stop is hit (only if trailing active)
        if self.trailing_active and pnl <= active_stop:
            return True

        return False

    def status(self):
        return {
            "pnl": self.pnl,
            "tp": self.tp,
            "sl": self.sl,
            "trail_range": self.trail_range,
            "trailing_active": self.trailing_active,
            "new_max": self.new_max,
            "cutoff": self.cutoff,
            "active_stop": self.cutoff if self.trailing_active else None,
        }

    def is_trailing_active(self) -> bool:
        return self.trailing_active