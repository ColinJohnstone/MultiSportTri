import json
from datetime import datetime, timedelta

def add_hal_higdon_runs(file_path="training_plan.json"):
    try:
        with open(file_path, 'r') as f:
            current_plan = json.load(f)
    except FileNotFoundError:
        current_plan = []

    # Hal Higdon Intermediate 1 Sunday Long Runs (in miles)
    # Week 18 is "Marathon", so we add 17 long run entries.
    higdon_long_runs_miles = [
        8, 9, 6, 11, 12, 9, 14, 15, 13, 17, 18, 13, 20, 12, 20, 12, 8
    ]

    # Determine the start date for the Hal Higdon plan
    # Triathlon is August 17, 2025 (Sunday)
    # First Hal Higdon Sunday long run is August 24, 2025
    start_date_higdon = datetime(2025, 8, 24)

    # Determine the starting week number for the new entries
    max_existing_week = 0
    if current_plan:
        # Ensure 'week' key exists and is an integer for all entries before finding max
        valid_weeks = [entry.get('week', 0) for entry in current_plan if isinstance(entry.get('week'), int)]
        if valid_weeks:
            max_existing_week = max(valid_weeks)
    
    # The new runs start the week *after* the last existing week that contains the triathlon.
    # Let's find the week of the triathlon (2025-08-17) to be more precise.
    triathlon_date_str = "2025-08-17"
    triathlon_week = max_existing_week # Default to max if triathlon date not found or no week associated
    
    for entry in current_plan:
        if entry.get('date') == triathlon_date_str and isinstance(entry.get('week'), int):
            triathlon_week = entry.get('week')
            break
            
    current_higdon_week_number_offset = 1 # Start HH weeks from 1

    new_workouts = []
    for i, miles in enumerate(higdon_long_runs_miles):
        run_date = start_date_higdon + timedelta(weeks=i)
        run_date_str = run_date.strftime('%Y-%m-%d')
        
        # Calculate the overall week number
        # This assumes the HH plan starts the week *after* the triathlon_week.
        # So, the first HH run is in `triathlon_week + 1`, the second in `triathlon_week + 2`, etc.
        overall_week_number = triathlon_week + current_higdon_week_number_offset
        current_higdon_week_number_offset +=1

        workout_entry = {
            "week": overall_week_number,
            "dayOfWeek": "Sunday",
            "date": run_date_str,
            "activityType": "Run",
            "title": f"Marathon Training: {miles} Mile Long Run",
            "details": "Hal Higdon Intermediate 1 Marathon Training Plan - Sunday Long Run."
        }
        new_workouts.append(workout_entry)

    # Add new workouts to the plan, replacing if date already exists (unlikely for these future dates)
    # More robustly, we should ensure no duplicates by date before appending.
    existing_dates = {entry['date'] for entry in current_plan}
    for workout in new_workouts:
        if workout['date'] not in existing_dates:
            current_plan.append(workout)
        else:
            # If a workout for this date already exists, update it.
            # This is a simplistic update; more sophisticated merging might be needed in other scenarios.
            for i, entry in enumerate(current_plan):
                if entry['date'] == workout['date']:
                    current_plan[i] = workout
                    break
    
    # Sort the entire plan by date
    current_plan.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))

    return json.dumps(current_plan, indent=4)

if __name__ == "__main__":
    # This script is now designed to add Hal Higdon runs.
    # The previous functionality of modifying specific entries (like Test or Race day)
    # has been removed to focus on this task.
    # If you need to re-run previous modifications, use the script from that specific subtask.
    
    # For this subtask, we directly call the function that adds Hal Higdon runs.
    # The previous script `process_training_plan.py` had different logic.
    # This version of `process_training_plan.py` should be:
    
    # import json
    # from datetime import datetime, timedelta

    # def add_hal_higdon_runs(file_path="training_plan.json"):
    #     # ... (implementation as above) ...
    #     pass # Placeholder for the actual function body

    # if __name__ == "__main__":
    #    modified_json = add_hal_higdon_runs()
    #    print(modified_json)
    
    # The code provided in the thought block will be written to process_training_plan.py
    # So, the __main__ block should just call the primary function of this script.
    
    output_json = add_hal_higdon_runs()
    print(output_json)
