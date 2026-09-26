class Job:
    def __init__(self):
        self.status = "pending"
        self.sends = 0

async def deliver(job, before_claim):
    if job.status != "pending":
        return False
    await before_claim()
    job.status = "claimed"
    job.sends += 1
    return True
