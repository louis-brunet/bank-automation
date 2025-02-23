class MaxRetriesExceededError(ValueError):
    def __init__(self, try_count: int) -> None:
        super().__init__(f'max retries exceeded: {try_count}')
