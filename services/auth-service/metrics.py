from prometheus_client import Counter, Gauge, Histogram

auth_requests_total = Counter(
    "auth_requests_total",
    "Total number of authentication requests",
    ["method", "status"]
)

auth_failures_total = Counter(
    "auth_failures_total",
    "Total number of failed authentication requests",
    ["reason"]
)

active_users_gauge = Gauge(
    "active_users",
    "Number of currently active users"
)

request_duration_seconds = Histogram(
    "auth_request_duration_seconds",
    "Duration of authentication requests",
    ["endpoint"]
)
