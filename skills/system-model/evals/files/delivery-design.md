# Proposed delivery workflow

There is no implementation yet. Two workers may pick one pending delivery.
A worker reads its status, then separately writes claimed, sends a notification
through a remote service, and records sent. A worker can crash after any step.
A notification can be accepted remotely even if its response is lost. Recovery
returns an unfinished claim to pending. The service currently has no documented
idempotency contract. We are considering adding a stable delivery ID that the
remote service promises to deduplicate across all retries.

Requirements:
- A delivery must cause at most one remote notification.
- A pending delivery should eventually be sent when workers continue retrying,
  crashes eventually stop and the remote service eventually responds.
- We need to understand which guarantees each design can actually support.
