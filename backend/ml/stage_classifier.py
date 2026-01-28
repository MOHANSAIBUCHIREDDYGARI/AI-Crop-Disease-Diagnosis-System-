def classify_stage(severity):
    if severity < 10:
        return "Healthy Stage"
    elif severity < 30:
        return "Early Stage"
    elif severity < 60:
        return "Moderate Stage"
    else:
        return "Severe Stage"
