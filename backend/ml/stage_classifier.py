def classify_stage(severity):
    """
    Decides the stage of the disease based on how severe it looks.
    Like a doctor saying 'It's just the beginning' or 'It's advanced'.
    """
    if severity < 10:
        return "Healthy Stage"   # Barely any signs
    elif severity < 30:
        return "Early Stage"     # Just starting to show spots
    elif severity < 60:
        return "Moderate Stage"  # It's spreading
    else:
        return "Severe Stage"    # Most of the leaf is affected
