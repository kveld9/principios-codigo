"""Explicit state machine: sealed state variants with single transition function.

This module models an asynchronous background sync job using an explicit finite
state machine. Every operational phase is represented by an immutable state
dataclass carrying only data valid in that phase. Transitions are handled by a
single deterministic function that rejects illegal transitions fail-loud.
"""

from dataclasses import dataclass
from typing import Any


class IllegalStateTransitionError(RuntimeError):
    """Raised when an event cannot be applied to the current operational state."""


# --- Immutable State Variants (Sum Type) ---


@dataclass(frozen=True)
class IdleState:
    """Initial or reset state when no sync job is active."""


@dataclass(frozen=True)
class RunningState:
    """State indicating an active sync job in progress."""

    job_id: str
    started_at: float


@dataclass(frozen=True)
class CompletedState:
    """Terminal state containing validated synchronization results."""

    job_id: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class FailedState:
    """Terminal state recording a failed sync attempt and failure cause."""

    job_id: str
    error_message: str


@dataclass(frozen=True)
class CancelledState:
    """Terminal state recording explicit cancellation and reason."""

    job_id: str
    reason: str


SyncState = IdleState | RunningState | CompletedState | FailedState | CancelledState


# --- Domain Events ---


@dataclass(frozen=True)
class StartSync:
    """Event requesting sync initialization."""

    job_id: str
    started_at: float


@dataclass(frozen=True)
class FinishSync:
    """Event reporting successful worker execution."""

    payload: dict[str, Any]


@dataclass(frozen=True)
class FailSync:
    """Event reporting worker execution failure."""

    error_message: str


@dataclass(frozen=True)
class CancelSync:
    """Event requesting immediate sync cancellation."""

    reason: str = "User cancelled"


@dataclass(frozen=True)
class ResetSync:
    """Event requesting cleanup and return to Idle state."""


SyncEvent = StartSync | FinishSync | FailSync | CancelSync | ResetSync


# --- Transition Handlers (CC <= 4 per handler) ---


def _transition_from_idle(event: SyncEvent) -> SyncState:
    """Handle transitions departing from IdleState."""
    if isinstance(event, StartSync):
        return RunningState(job_id=event.job_id, started_at=event.started_at)
    raise IllegalStateTransitionError(f"Cannot apply {type(event).__name__} from IdleState")


def _transition_from_running(state: RunningState, event: SyncEvent) -> SyncState:
    """Handle transitions departing from RunningState."""
    if isinstance(event, FinishSync):
        return CompletedState(job_id=state.job_id, payload=event.payload)
    if isinstance(event, FailSync):
        return FailedState(job_id=state.job_id, error_message=event.error_message)
    if isinstance(event, CancelSync):
        return CancelledState(job_id=state.job_id, reason=event.reason)
    raise IllegalStateTransitionError(f"Cannot apply {type(event).__name__} from RunningState")


def _transition_from_terminal(
    state: CompletedState | FailedState | CancelledState,
    event: SyncEvent,
) -> SyncState:
    """Handle transitions departing from terminal states."""
    if isinstance(event, ResetSync):
        return IdleState()
    raise IllegalStateTransitionError(
        f"Cannot apply {type(event).__name__} from {type(state).__name__}"
    )


def transition(current_state: SyncState, event: SyncEvent) -> SyncState:
    """Transition pure function: (current_state, event) -> next_state."""
    match current_state:
        case IdleState():
            return _transition_from_idle(event)
        case RunningState():
            return _transition_from_running(current_state, event)
        case CompletedState() | FailedState() | CancelledState():
            return _transition_from_terminal(current_state, event)


class ExplicitSyncCoordinator:
    """Single owner of sync lifecycle state."""

    def __init__(self) -> None:
        self._state: SyncState = IdleState()

    @property
    def state(self) -> SyncState:
        """Inspect current immutable state."""
        return self._state

    def dispatch(self, event: SyncEvent) -> SyncState:
        """Apply an event through the single transition function."""
        self._state = transition(self._state, event)
        return self._state
