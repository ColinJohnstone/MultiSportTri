import json

def verify_race_entry(file_path="training_plan.json"):
    try:
        with open(file_path, 'r') as f:
            plan = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File '{file_path}' not found.")
        return

    race_date = "2025-08-17"
    expected_activity_type = "Race"
    expected_title = "Toronto Island Multisport Triathlon"

    entry_found = False
    for entry in plan:
        if entry.get("date") == race_date:
            entry_found = True
            actual_activity_type = entry.get("activityType")
            actual_title = entry.get("title")

            type_correct = actual_activity_type == expected_activity_type
            title_correct = actual_title == expected_title

            if type_correct and title_correct:
                print(f"SUCCESS: Entry for {race_date} is correctly labeled.")
                print(f"  Activity Type: '{actual_activity_type}' (Expected: '{expected_activity_type}')")
                print(f"  Title: '{actual_title}' (Expected: '{expected_title}')")
            else:
                print(f"ERROR: Discrepancy found for entry on {race_date}:")
                if not type_correct:
                    print(f"  Activity Type: '{actual_activity_type}' (Expected: '{expected_activity_type}')")
                else:
                    print(f"  Activity Type: '{actual_activity_type}' (Correct)")
                
                if not title_correct:
                    print(f"  Title: '{actual_title}' (Expected: '{expected_title}')")
                else:
                    print(f"  Title: '{actual_title}' (Correct)")
            return

    if not entry_found:
        print(f"ERROR: No entry found for date {race_date}.")

if __name__ == "__main__":
    verify_race_entry()
