def format_confidence(confidence):
    """
    Make the score look nice (e.g., 98.54321% -> 98.54 %)
    """
    return f"{round(confidence, 2)} %"
