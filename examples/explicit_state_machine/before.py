"""Anti-pattern: Implicit state machine with loose flags and nullable buffers.

This module models an asynchronous background sync job using uncoordinated
boolean flags and nullable buffers. Concurrent events, reordered callbacks,
or cancellation races lead to impossible state combinations, stale buffers,
and silent corruption.
"""

from typing import Any


class ImplicitSyncJob:
    """Sync job coordinator governed by loose flags and nullable sentinels."""

    def __init__(self) -> None:
        self.is_running: bool = False
        self.is_completed: bool = False
        self.is_cancelled: bool = False
        self.has_error: bool = False
        self.job_id: str | None = None
        self.data_buffer: dict[str, Any] | None = None
        self.error_message: str | None = None

    def start(self, job_id: str) -> None:
        """Start a sync job without verifying whether one is already running."""
        # Defect: Can be called while already running, silently mutating job_id
        self.job_id = job_id
        self.is_running = True
        self.is_completed = False
        self.is_cancelled = False
        self.has_error = False

    def finish(self, payload: dict[str, Any]) -> None:
        """Accept completed payload from an asynchronous worker."""
        # Defect: Accepts payload even if the job was previously cancelled or failed
        self.is_running = False
        self.is_completed = True
        self.data_buffer = payload

    def cancel(self, reason: str = "User cancelled") -> None:
        """Cancel ongoing sync process."""
        # Defect: Does not cancel running worker callbacks or reset data buffers
        self.is_running = False
        self.is_cancelled = True
        self.error_message = reason

    def fail(self, error: str) -> None:
        """Record sync failure."""
        # Defect: Leaves stale data_buffer intact if previously set
        self.is_running = False
        self.has_error = True
        self.error_message = error

    def is_inconsistent(self) -> bool:
        """Detect whether the internal flags have reached an impossible state."""
        # An inconsistent state occurs when contradictory flags are simultaneously true
        multiple_terminal_states = sum([self.is_completed, self.is_cancelled, self.has_error]) > 1
        running_with_terminal = self.is_running and (
            self.is_completed or self.is_cancelled or self.has_error
        )
        completed_without_data = self.is_completed and self.data_buffer is None
        return multiple_terminal_states or running_with_terminal or completed_without_data
