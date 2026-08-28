def add_loopback_hosts(allowed_hosts: list[str], app_port: str) -> list[str]:
    """Append the loopback hosts Docker/Coolify healthchecks need to allowed_hosts, in place.

    Two independent healthcheck mechanisms hit the container over loopback with different
    hosts: the Dockerfile's own HEALTHCHECK curls 127.0.0.1, while Coolify's built-in
    container healthcheck (not configurable) execs against localhost. Both need the bare
    host and the "host:port" form, since HttpRequest.get_host() strips the port before
    matching ALLOWED_HOSTS but the Host header itself carries it.
    """
    for loopback_host in ("127.0.0.1", f"127.0.0.1:{app_port}", "localhost", f"localhost:{app_port}"):
        if loopback_host not in allowed_hosts:
            allowed_hosts.append(loopback_host)
    return allowed_hosts
