    assert call_kwargs()["status_count_all"] == 3


def test_reset_filters_clears_session_cookies(admin_client):
    """Test that passing reset_filters=true clears session filter cookies."""
    with admin_client.session_transaction() as session:
        session["last_run_filter"] = "running"
        session["tags_filter"] = "example"
        session["dag_status_filter"] = "active"

    response = admin_client.get("/home?reset_filters=true", follow_redirects=False)
    
    # Asserts 302 redirect back to clean /home
    assert response.status_code == 302
    assert response.location == "/home"

    # Asserts session cookies are cleared
    with admin_client.session_transaction() as session:
        assert session.get("last_run_filter") is None
        assert session.get("tags_filter") is None
        assert session.get("dag_status_filter") is None


def test_home_status_filter_cookie(admin_client):
    with admin_client:
        admin_client.get("home", follow_redirects=True)
