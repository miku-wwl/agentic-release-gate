"""Bounded HTTP service behind the existing Azure managed ingress."""

bind = "0.0.0.0:8080"
workers = 1
worker_class = "gthread"
threads = 4
worker_connections = 16
backlog = 32
timeout = 75
graceful_timeout = 6
keepalive = 2
limit_request_line = 1024
limit_request_fields = 40
limit_request_field_size = 4096
worker_tmp_dir = "/tmp"
forwarded_allow_ips = ""
forwarder_headers = []
secure_scheme_headers = {}
control_socket_disable = True
accesslog = None
errorlog = "-"
loglevel = "warning"
umask = 0o077
