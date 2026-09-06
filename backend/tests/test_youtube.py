from app.pipeline.youtube import is_allowed_youtube_url


def test_allows_standard_youtube_url():
    assert is_allowed_youtube_url("https://www.youtube.com/watch?v=abc123")


def test_allows_bare_youtube_host():
    assert is_allowed_youtube_url("https://youtube.com/watch?v=abc123")


def test_allows_short_youtu_be_url():
    assert is_allowed_youtube_url("https://youtu.be/abc123")


def test_rejects_non_youtube_host():
    assert not is_allowed_youtube_url("https://evil.example.com/watch?v=abc123")


def test_rejects_lookalike_host():
    # A naive substring/suffix check could be tricked by a host like this.
    assert not is_allowed_youtube_url("https://youtube.com.evil.example.com/watch?v=abc123")


def test_rejects_malformed_url():
    assert not is_allowed_youtube_url("not a url")
