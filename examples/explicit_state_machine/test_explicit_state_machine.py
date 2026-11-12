"""Tests verifying explicit state machine invariants and illegal transition rejection."""

import pytest

from examples.explicit_state_machine.after import (
    CancelledState,
    CancelSync,
    CompletedState,
    ExplicitSyncCoordinator,
    FailedState,
    FailSync,
    FinishSync,
    IdleState,
    IllegalStateTransitionError,
    ResetSync,
    RunningState,
    StartSync,
    transition,
)
from examples.explicit_state_machine.before import ImplicitSyncJob


def test_happy_path_lifecycle_idle_to_completed() -> None:
    """A sync job proceeds deterministically from Idle through Running to Completed."""
    coordinator = ExplicitSyncCoordinator()
    assert isinstance(coordinator.state, IdleState)

    coordinator.dispatch(StartSync(job_id="job-101", started_at=1000.0))
    assert coordinator.state == RunningState(job_id="job-101", started_at=1000.0)

    coordinator.dispatch(FinishSync(payload={"records_synced": 42}))
    assert coordinator.state == CompletedState(
        job_id="job-101",
        payload={"records_synced": 42},
    )

    coordinator.dispatch(ResetSync())
    assert isinstance(coordinator.state, IdleState)


def test_failure_lifecycle_records_error_and_allows_reset() -> None:
    """A failed sync records failure reason without residual payload and can be reset."""
    coordinator = ExplicitSyncCoordinator()
    coordinator.dispatch(StartSync(job_id="job-102", started_at=1005.0))
    coordinator.dispatch(FailSync(error_message="Connection timed out"))

    assert coordinator.state == FailedState(
        job_id="job-102",
        error_message="Connection timed out",
    )

    coordinator.dispatch(ResetSync())
    assert isinstance(coordinator.state, IdleState)


def test_cancellation_lifecycle_preserves_reason() -> None:
    """Cancellation transitions Running to Cancelled with reason."""
    coordinator = ExplicitSyncCoordinator()
    coordinator.dispatch(StartSync(job_id="job-103", started_at=1010.0))
    coordinator.dispatch(CancelSync(reason="User clicked cancel"))

    assert coordinator.state == CancelledState(
        job_id="job-103",
        reason="User clicked cancel",
    )


@pytest.mark.parametrize(
    ("initial_state", "illegal_event"),
    [
        (IdleState(), FinishSync(payload={"data": 1})),
        (IdleState(), FailSync(error_message="Error")),
        (IdleState(), CancelSync()),
        (IdleState(), ResetSync()),
        (RunningState(job_id="job-1", started_at=1.0), StartSync(job_id="job-2", started_at=2.0)),
        (RunningState(job_id="job-1", started_at=1.0), ResetSync()),
        (CompletedState(job_id="job-1", payload={}), StartSync(job_id="job-2", started_at=2.0)),
        (CompletedState(job_id="job-1", payload={}), FinishSync(payload={})),
        (CancelledState(job_id="job-1", reason="Stopped"), FinishSync(payload={})),
        (FailedState(job_id="job-1", error_message="Fatal"), FailSync(error_message="Duplicate")),
    ],
)
def test_illegal_state_transitions_raise_fail_loud(
    initial_state: IdleState | RunningState | CompletedState | CancelledState | FailedState,
    illegal_event: StartSync | FinishSync | FailSync | CancelSync | ResetSync,
) -> None:
    """Every illegal event for a given state variant is rejected with an exception."""
    with pytest.raises(IllegalStateTransitionError):
        transition(initial_state, illegal_event)


def test_implicit_job_permits_corrupted_state_after_cancellation() -> None:
    """Before: An uncoordinated job reaches an inconsistent state on delayed callbacks."""
    implicit_job = ImplicitSyncJob()
    implicit_job.start("job-race-01")
    implicit_job.cancel("User cancelled")
    implicit_job.finish({"stale": "payload"})

    assert implicit_job.is_cancelled is True
    assert implicit_job.is_completed is True
    assert implicit_job.is_inconsistent() is True


def test_explicit_coordinator_rejects_stale_completion_after_cancellation() -> None:
    """After: The coordinator rejects delayed worker callbacks once cancelled."""
    explicit_job = ExplicitSyncCoordinator()
    explicit_job.dispatch(StartSync(job_id="job-race-01", started_at=2000.0))
    explicit_job.dispatch(CancelSync(reason="User cancelled"))

    with pytest.raises(IllegalStateTransitionError):
        explicit_job.dispatch(FinishSync(payload={"stale": "payload"}))

    assert isinstance(explicit_job.state, CancelledState)
    assert explicit_job.state.reason == "User cancelled"
