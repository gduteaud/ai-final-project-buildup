
def greet(name):
    """Return a friendly greeting."""
    if name:
        name = name.strip()
    return f"Hello, {name or 'there'}!"