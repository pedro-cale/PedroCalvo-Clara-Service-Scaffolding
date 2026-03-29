from app.main import tick


def test_tick() -> None:
    assert tick() == "ok"
