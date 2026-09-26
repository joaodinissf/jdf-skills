# Worker contract
All callers run on one cooperative asyncio event loop and share the same Job.
The callback before_claim may suspend. The in-memory sends increment represents
a synchronous side effect with no failure or suspension in this fixture. A Job
must be sent at most once, even when multiple callers try to deliver it. There
are no threads, other processes, crashes or remote services in this contract.
