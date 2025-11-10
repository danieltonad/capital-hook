class TrailingSL:
    def __init__(self, pnl: float, tp: float, sl: float, trail_range: float):
        self.pnl = pnl
        self.tp = tp
        self.sl = -abs(sl)  # ensure it's negative
        self.trail_range = trail_range

        self.new_max = pnl
        self.cutoff = self.sl  # cutoff starts at SL

    def _pick_stop(self) -> float:
        """Choose the correct active stop based on sign logic."""
        if self.sl < 0 and self.cutoff < 0:
            return min(self.sl, self.cutoff)  # pick more negative one
        return max(self.sl, self.cutoff)  # otherwise take the higher one

    def update_pnl(self, pnl: float) -> bool:
        """
        Update PnL and check exit conditions.
        Returns:
            bool: True if TP or SL hit, False otherwise.
        """
        self.pnl = pnl

        # Only trail when in profit
        if pnl > 0 and pnl > self.new_max:
            self.new_max = pnl
            self.cutoff = max(self.cutoff, self.new_max - self.trail_range)

        # Check TP hit
        if pnl >= self.tp:
            return True

        # Check SL or trailing stop hit (using new rule)
        if pnl <= self._pick_stop():
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
            "active_stop": self._pick_stop(),
        }
