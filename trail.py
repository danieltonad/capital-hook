class TrailingSL:
    def __init__(self, pnl: float, tp: float, sl: float, trail_range: float):
        self.pnl = pnl
        self.tp = tp
        self.sl = -sl
        self.trail_range = trail_range

        self.new_max = pnl
        self.cutoff = pnl - trail_range

    def update_pnl(self, pnl: float) -> bool:
        """
        Update PnL and check exit conditions.
        Returns:
            bool: True if TP or SL hit, False otherwise.
        """
        self.pnl = pnl

        # Update trailing max and cutoff if PnL increases
        if pnl > self.new_max:
            self.new_max = pnl
            self.cutoff = self.new_max - self.trail_range

        # Check TP hit
        if pnl >= self.tp:
            return True

        # Check SL or trailing stop hit
        if pnl <= max(self.sl, self.cutoff):
            return True

        return False

    def status(self) -> dict:
        """Return current trailing state."""
        return {
            "pnl": self.pnl,
            "tp": self.tp,
            "sl": self.sl,
            "trail_range": self.trail_range,
            "new_max": self.new_max,
            "cutoff": self.cutoff,
        }
