class TransientError(Exception):
    pass


def deliver(message, send, max_retries=2):
    """Send a message, retrying on transient errors.

    `send` returns normally on success and raises TransientError on a
    transient failure. A failure after the remote accepted the message is
    reported as transient too.
    """
    attempts_left = max_retries
    while True:
        try:
            send(message)
            return True
        except TransientError as err:
            if getattr(err, "throttled", False):
                attempts_left = max_retries  # back off and start over
                continue
            if attempts_left == 0:
                return False
            attempts_left -= 1
