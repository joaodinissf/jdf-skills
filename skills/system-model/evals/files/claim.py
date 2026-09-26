import asyncio


class Job:
    def __init__(self):
        self.status = "pending"
        self.sends = 0


async def claim_and_send(job, lease_service):
    if job.status != "pending":
        return False
    await lease_service.acquire(job)
    job.status = "claimed"
    job.sends += 1
    return True
