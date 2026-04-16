# import pybreaker

# rabbitmq_breaker = pybreaker.CircuitBreaker(
#     fail_max=5,
#     reset_timeout=30,
#     name="rabbitmq-publisher"
# )

import pybreaker

rabbitmq_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=60,
    name="rabbitmq-publisher",
)