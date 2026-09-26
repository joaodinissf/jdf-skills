# Claim contract
Callers run on one asyncio event loop and share one Job. `lease_service.acquire`
may suspend. A Job must be sent at most once, however many callers try.
