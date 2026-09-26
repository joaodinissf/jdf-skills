from dataclasses import dataclass

@dataclass(frozen=True)
class State:
    phase: str = "idle"
    starts: int = 0

def step(state, event):
    if event == "start" and state.phase == "idle":
        return State("running", state.starts + 1)
    if event == "finish" and state.phase == "running":
        return State("done", state.starts)
    if event == "cancel" and state.phase in {"idle", "running"}:
        return State("cancelled", state.starts)
    return state
