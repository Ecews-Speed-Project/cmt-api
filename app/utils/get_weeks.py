from datetime import date, timedelta

def get_weeks_between_dates(start_date_str, end_date_str):
    """
    Returns a list of dictionaries representing the weeks between two dates.

    Args:
        start_date_str (str): The start date in 'YYYY-MM-DD' format.
        end_date_str (str): The end date in 'YYYY-MM-DD' format.

    Returns:
        list: A list of dictionaries, where each dictionary represents a week
              and contains the title, start date, and end date.
    """
    start_date = date.fromisoformat(start_date_str)
    end_date = date.fromisoformat(end_date_str)
    weeks = []
    current_date = start_date
    week_number = 1

    while current_date <= end_date:
        week_start = current_date
        week_end = current_date + timedelta(days=6)
        if week_end > end_date:
            week_end = end_date

        weeks.append({
            "title": f"week{week_number}",
            "start": week_start.isoformat(),
            "end": week_end.isoformat()
        })

        current_date = week_end + timedelta(days=1)
        week_number += 1

    return weeks