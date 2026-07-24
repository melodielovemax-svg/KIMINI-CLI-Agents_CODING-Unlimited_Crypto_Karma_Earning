"""
IMPACT SCORING VISUALIZATION
Green for Positive / Red for Negative
"""

from datetime import datetime


def score_to_visual(score, is_positive, is_negative, dimensions):
    """Build visual impact data for rendering."""
    if score > 0:
        color = "green"
        label = "POSITIVE"
        bar_char = "#"
        bar_color = "bright_green"
    elif score < 0:
        color = "red"
        label = "NEGATIVE"
        bar_char = "!"
        bar_color = "bright_red"
    else:
        color = "white"
        label = "NEUTRAL"
        bar_char = "."
        bar_color = "white"

    magnitude = min(abs(score), 100)
    bar_len = int(magnitude / 5)
    bar = bar_char * bar_len + "." * (20 - bar_len)

    dim_rows = []
    for name, data in sorted(dimensions.items(), key=lambda x: -abs(x[1]["score"])):
        dim_score = data["score"]
        if dim_score > 0:
            dim_color = "bright_green"
            dim_bar = "#" * min(int(dim_score / 2), 15) + "." * max(0, 15 - int(dim_score / 2))
        else:
            dim_color = "bright_red"
            dim_bar = "!" * min(int(abs(dim_score) / 2), 15) + "." * max(0, 15 - int(abs(dim_score) / 2))
        dim_rows.append({
            "name": name,
            "icon": data.get("icon", "???"),
            "desc": data.get("desc", ""),
            "score": dim_score,
            "color": dim_color,
            "bar": dim_bar,
        })

    return {
        "color": color,
        "label": label,
        "bar": bar,
        "bar_color": bar_color,
        "score": score,
        "magnitude": magnitude,
        "dimensions": dim_rows,
        "timestamp": datetime.utcnow().isoformat(),
    }
