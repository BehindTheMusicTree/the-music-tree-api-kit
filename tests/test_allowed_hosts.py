from the_music_tree_api_kit.utils.allowed_hosts import add_loopback_hosts


def test_appends_all_four_loopback_variants():
    allowed_hosts = ["example.com"]

    result = add_loopback_hosts(allowed_hosts, app_port="8000")

    assert result == ["example.com", "127.0.0.1", "127.0.0.1:8000", "localhost", "localhost:8000"]


def test_does_not_duplicate_hosts_already_present():
    allowed_hosts = ["example.com", "localhost"]

    result = add_loopback_hosts(allowed_hosts, app_port="8000")

    assert result == ["example.com", "localhost", "127.0.0.1", "127.0.0.1:8000", "localhost:8000"]


def test_mutates_and_returns_the_same_list():
    allowed_hosts = []

    result = add_loopback_hosts(allowed_hosts, app_port="8000")

    assert result is allowed_hosts
