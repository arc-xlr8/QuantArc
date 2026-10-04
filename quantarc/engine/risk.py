from __future__ import annotations


class RiskManager:
    """Position sizing and protective exits (long-only).

    position_fraction: share of available cash committed per entry (0-1].
    stop_loss / take_profit: fractional distance from entry (e.g. 0.05 = 5%).
    allow_fractional: allow fractional share quantities.
    """

    def __init__(self, position_fraction: float = 1.0, stop_loss: float | None = None,
                 take_profit: float | None = None, allow_fractional: bool = False):
        if not 0 < position_fraction <= 1:
            raise ValueError("position_fraction must be in (0, 1]")
        self.position_fraction = position_fraction
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.allow_fractional = allow_fractional

    def position_size(self, max_affordable: float) -> float:
        qty = max_affordable * self.position_fraction
        return qty if self.allow_fractional else float(int(qty))

    def check_exit(self, entry_price: float, bar_open: float, bar_high: float,
                   bar_low: float) -> tuple[float, str] | None:
        """Return (exit_price, reason) if a protective level was hit inside the bar.
        Gaps through a level fill at the open. Stop wins if both are hit."""
        if self.stop_loss is not None:
            stop = entry_price * (1 - self.stop_loss)
            if bar_low <= stop:
                return min(bar_open, stop), "stop_loss"
        if self.take_profit is not None:
            target = entry_price * (1 + self.take_profit)
            if bar_high >= target:
                return max(bar_open, target), "take_profit"
        return None
