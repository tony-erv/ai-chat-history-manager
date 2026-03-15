def validate_message(text):
    """Check if the message is non-empty and under 2000 characters."""
    return bool(text) and len(text) < 2000