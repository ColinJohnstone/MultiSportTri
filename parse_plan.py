import re
import json
from datetime import datetime, timedelta

def parse_training_plan(text):
    plan = []
    current_date = datetime(2025, 5, 26)  # Start date: Monday, May 26, 2025
    day_of_week_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Remove introductory text
    text = text.split("12 Week Sprint Training Plan")[1]

    week_sections = re.split(r"Week (\d+)", text)[1:]

    for i in range(0, len(week_sections), 2):
        week_number = int(week_sections[i])
        week_content = week_sections[i+1].strip()
        
        lines = week_content.split('\n')
        
        current_day_activities = []
        activity_lines = []
        current_day_name = None

        line_idx = 0
        while line_idx < len(lines):
            line = lines[line_idx].strip()

            if line in day_of_week_map: # Found a day marker
                # Process previous day's activity if any
                if current_day_name and activity_lines:
                    title = activity_lines[0]
                    details = "\n".join(activity_lines[1:]).strip()
                    
                    # Handle if "Day Off" is title and details are empty, or details are on the next line
                    if title == "Day Off" and not details:
                        # Check if next line is part of details or a new day
                        if line_idx + 1 < len(lines) and lines[line_idx+1].strip() not in day_of_week_map and lines[line_idx+1].strip() != "":
                             # This was handled by the general logic, but explicit "Day Off" needs care
                             pass # details would have been captured if present

                    current_day_activities.append({
                        "dayOfWeek": current_day_name,
                        "title_raw": title, # temporary storage for multi-line titles/details
                        "details_raw": details
                    })
                    activity_lines = []

                current_day_name = line
                activity_lines = [] # Reset for new day
            elif current_day_name and line: # Collect lines for the current day
                activity_lines.append(line)
            
            line_idx += 1

        # Process the last activity of the week
        if current_day_name and activity_lines:
            title = activity_lines[0]
            details = "\n".join(activity_lines[1:]).strip()
            current_day_activities.append({
                "dayOfWeek": current_day_name,
                "title_raw": title,
                "details_raw": details
            })

        # Now, map these to the full structure with dates and activity types
        day_index_in_week = 0
        for activity_data in current_day_activities:
            day_of_week_str = activity_data["dayOfWeek"]
            
            # Ensure we align with the actual day of the week for date assignment
            while day_of_week_map[current_date.weekday()] != day_of_week_str:
                # This implies a missing day in the text, like a Monday Day Off not explicitly listed initially
                # Or we need to advance the date if the text skips days (e.g. Monday -> Wednesday)
                # For this plan, "Day Off" for Monday is usually listed.
                # If the first day of the week in text isn't Monday, we might have issues.
                # The prompt implies all days are covered or are "Day Off".

                # Add implicit "Day Off" if the text skips a day
                # This case should not happen if all Mondays are "Day Off" and listed
                if day_of_week_map[current_date.weekday()] not in [a['dayOfWeek'] for a in current_day_activities]:
                     # This logic is tricky; assuming the text provides all necessary entries.
                     # The problem is that current_date advances per *parsed* entry, not per actual day.
                     pass


            title = activity_data["title_raw"]
            details = activity_data["details_raw"]
            
            # If title is "Day Off" and details are empty, check if subsequent lines were meant as details
            # This is tricky because the initial split might have already separated them.
            # The current logic: title is the first line, rest are details.
            if title == "Day Off" and not details.strip() and day_of_week_str == "Monday":
                # Week 1 Monday: "Day Off" \n "Take the day off..."
                # Week 2 Monday: "Day Off" (no further details on separate lines before next day)
                # Week 4 Monday: "Day Off" \n "Take the day off..."
                # This should be handled by how activity_lines are joined.
                # Let's ensure specific "Day Off" detail assignment for Mondays if necessary
                if week_number in [1, 4] and day_of_week_str == "Monday":
                    # The details are correctly captured if they follow "Day Off" on subsequent lines.
                    # If details were "Take the day off..." it's fine.
                    # If details were empty, and it's W1/W4 Monday, it means the details were not captured.
                    # This needs careful check of how `activity_lines` are formed.
                     if not details: # Explicitly set for these weeks if somehow missed
                        details = "Take the day off, including as much time off your feet as possible.\nSpend some time preparing meals for the week, as well as arranging work\nand family schedules to best allow for succesful completion of assigned\nworkouts."

            activity_type = "Unknown" # Default

            if title == "Day Off":
                activity_type = "Rest"
                if not details: # Generic detail if none provided and not a special Monday
                    details = "Take the day off."
            elif "Swim Test" in title or "Run Test" in title or "Bike Test" in title:
                activity_type = "Test"
            elif "Swim" in title:
                activity_type = "Swim"
            elif "Bike" in title or "Ride" in title :
                activity_type = "Bike"
            elif "Run" in title:
                activity_type = "Run"
            
            # Specific corrections and activity type overrides
            if week_number == 3 and day_of_week_str == "Saturday":
                activity_type = "Brick"
                title = "60-Min Build Bike + 5-Min Run"
                # Details: "WU- 12 minutes easy MS- 4 x 9 minutes TP (test pace), with 2 minutes RI (recovery interval). Then run 5 minutes gradually building to TP. CD- 10 minutes easy"
                # The original details should be fine as they contain both parts.
            elif week_number == 5 and day_of_week_str == "Wednesday" and title == "45-Minute Easy Bike":
                details = "Ride easy/ conversational, and use an easy gear with a high cadence."
                activity_type = "Bike"
            elif week_number == 7 and day_of_week_str == "Thursday" and title == "50-Minute Build Ride":
                title = "50-Minute Build Run" # Corrected title
                activity_type = "Run"
                # Details: "WU- 10 minutes easy walk/ jog MS- 4 x 6 minutes TP (test pace), with 2 minutes RI (recovery interval). CD- 8 minutes easy walk/ jog" - these are run details
            elif week_number == 7 and day_of_week_str == "Saturday": # "65-Minute Build Bike ... Then run 8 minutes..."
                activity_type = "Brick"
                title = "65-Min Build Bike + 8-Min Run"
            elif week_number == 8 and day_of_week_str == "Saturday" and title == "30-Minute Easy Run":
                if not details.strip(): # If details are missing or just whitespace
                    details = "Run/walk easy (conversational), taking breaks as needed."
                activity_type = "Run"
            elif week_number == 10 and day_of_week_str == "Saturday": # "65-Minute Build Bike ... Then run 10 minutes..."
                activity_type = "Brick"
                title = "65-Min Build Bike + 10-Min Run"
            elif week_number == 12 and day_of_week_str == "Saturday": # "20-Minute Pre-Race Workout..."
                activity_type = "Brick"
                title = "20-Min Pre-Race Brick"
                # Details: "Bike 15 minutes progressing to race pace, then run 5 minutes progressing to race pace."
                # The script should capture this detail correctly from the input.
            elif week_number == 12 and day_of_week_str == "Sunday" and title == "RACE DAY":
                activity_type = "Race"
                # Details: "Arrive early, trust your sprint training plan, have fun!" - script should capture this
                # If details are empty for Race Day, add the specified one
                if not details.strip():
                    details = "Arrive early, trust your sprint training plan, have fun!"
            
            # Ensure Monday "Day Off" entries are captured even if just "Day Off" is listed
            # This is more about ensuring they are added to `plan`
            # The date advancement logic needs to be solid.

            # Find the expected day index for current_date
            expected_day_map_idx = current_date.weekday()
            # Find the index of the parsed day_of_week_str
            parsed_day_map_idx = day_of_week_map.index(day_of_week_str)

            # Add "Rest" days for any skipped days before the current parsed day
            while expected_day_map_idx < parsed_day_map_idx:
                # This means the text skipped a day (e.g. Monday is missing, Tuesday is first)
                # Add a "Day Off" for the actual day of the week.
                plan.append({
                    "week": week_number,
                    "dayOfWeek": day_of_week_map[expected_day_map_idx],
                    "date": current_date.strftime("%Y-%m-%d"),
                    "activityType": "Rest",
                    "title": "Day Off",
                    "details": "Take the day off." # Default for implicitly added rest day
                })
                current_date += timedelta(days=1)
                expected_day_map_idx = current_date.weekday()


            plan.append({
                "week": week_number,
                "dayOfWeek": day_of_week_str,
                "date": current_date.strftime("%Y-%m-%d"),
                "activityType": activity_type,
                "title": title,
                "details": details.strip() # Ensure details are stripped of leading/trailing whitespace
            })
            
            current_date += timedelta(days=1)
            day_index_in_week +=1

        # After processing all entries for a week, fill in any remaining days of that week if needed
        # (e.g. if Sunday was "Day Off" and not explicitly listed)
        # The current_date reflects the day *after* the last processed entry.
        # Its weekday() is now for the *next* day.
        # Example: If Sunday was the last processed day, current_date is now Monday of next week.
        # If Saturday was last, current_date is Sunday. We need to check if Sunday was processed.
        
        # Check if the week ended prematurely (e.g. last entry was Friday)
        # The loop `for activity_data in current_day_activities:` handles listed days.
        # This post-loop fill is for days at the *end* of the week that might be missing.
        # The `current_date.weekday()` is 0 (Monday) if a full week just ended and current_date incremented.
        # If it's not 0, it means the week didn't end on a Sunday or current_date didn't roll over.
        
        # Simplified: Ensure 7 entries per week by advancing date until next Monday
        # This assumes the input text has entries for each day that is NOT a "Day Off"
        # And "Day Off" entries are also explicitly listed.
        # The logic above for `while expected_day_map_idx < parsed_day_map_idx:` should handle intermediate missing days.
        # This part is to fill trailing "Day Off"s if the week's entries stop early.
        
        # If last processed day was not Sunday for this week
        if current_day_activities: # only if there were activities parsed for the week
            last_parsed_day_name = current_day_activities[-1]["dayOfWeek"]
            last_parsed_day_idx = day_of_week_map.index(last_parsed_day_name)
            
            while last_parsed_day_idx < 6: # 6 is Sunday's index
                last_parsed_day_idx += 1
                # current_date has already been incremented for the *next* day to be processed
                # So, if last_parsed_day_name was Saturday, current_date is for Sunday.
                plan.append({
                    "week": week_number,
                    "dayOfWeek": day_of_week_map[last_parsed_day_idx],
                    "date": current_date.strftime("%Y-%m-%d"),
                    "activityType": "Rest",
                    "title": "Day Off",
                    "details": "Take the day off." 
                })
                current_date += timedelta(days=1)


    return plan

training_plan_text = """
12 Week Super Simple Sprint Triathlon Training Plan

   You will enjoy progressing through each phase as you gain fitness and
   speed throughout each four-week cycle.
   Published Sep 26, 2018
   Scott Fliegelman

   This 12 week sprint triathlon training plan is ideal for beginner to
   intermediate triathletes who are currently able to complete a 15-minute
   swim (with breaks as needed), a 30-minute bike, and a 30-minute
   run/walk. You will find this plan quite easy to comprehend, and the
   rhythm of workouts each week, as well as from week to week, to be fun
   and achievable for even those with busy work or family commitments. You
   will enjoy progressing through assorted training ‘phases’, such as
   ‘test,’ ‘build,’ and ‘recover,’ and as such will be able to note
   improved fitness and speed throughout each four-week cycle.

12 Week Sprint Training Plan

Week 1

   Monday
   Day Off
   Take the day off, including as much time off your feet as possible.
   Spend some time preparing meals for the week, as well as arranging work
   and family schedules to best allow for succesful completion of assigned
   workouts.

   Tuesday
   30-Minute Swim Test
   WU- 5 to 10 minutes easy swim
   MS- Swim 15 minutes max distance… taking breaks if/ as needed.
   CD- 5 minutes easy swim

   Wednesday
   45-Minute Easy Bike
   Ride easy/ conversational, and use an easy gear with a high cadence.

   Thursday
   45-Minute Run Test
   WU- 10 minutes easy walk/ jog
   MS- Run/ walk 30 minutes maximum distance.
   CD- 5 minutes easy walk

   Friday
   20-Minute Easy Swim
   Swim easy, taking breaks as needed.

   Saturday
   45-Minute Bike Test
   WU- Ride 10 minutes easy
   MS- Ride 30 minutes maximum distance
   CD- Ride 5 minutes easy

   Sunday
   30-Minute Easy Run
   Run/ walk easy (conversational), taking breaks as needed.

Week 2

   Monday
   Day Off

   Tuesday
   25-Minute Build Swim
   WU- 5 minutes easy swim
   MS- 4 x 3 minutes TP (test pace), with 1 minute RI (recovery interval)
   CD- 5 minutes easy swim

   Wednesday
   45-Minute Easy Bike
   Ride easy/ conversational, and use an easy gear with a high cadence.

   Thursday
   40-Minute Build Run
   WU- 10 minutes easy walk/ jog
   MS- 4 x 4 minutes TP (test pace), with 2 minutes RI (recovery
   interval).
   CD- 8 minutes easy walk/ jog

   Friday
   20-Minute Easy Swim
   Swim easy, taking breaks as needed.

   Saturday
   60-Minute Build Bike
   WU- 12 minutes easy
   MS- 4 x 8 minutes TP (test pace), with 2 minutes RI (recovery
   interval).
   CD- 10 minutes easy

   Sunday
   30-Minute Easy Run
   Run/ walk easy (conversational), taking breaks as needed.

Week 3

   Monday
   Day Off

   Tuesday
   30-Minute Build Swim
   WU- 5 minutes easy swim
   MS- 4 x 4 minutes TP (test pace), with 1 minute RI (recovery interval)
   CD- 5 minutes easy swim

   Wednesday
   45-Minute Easy Bike
   Ride easy/ conversational, and use an easy gear with a high cadence.

   Thursday
   45-Minute Build Run
   WU- 10 minutes easy walk/ jog
   MS- 4 x 5 minutes TP (test pace), with 2 minutes RI (recovery
   interval).
   CD- 8 minutes easy walk/ jog

   Friday
   20-Minute Easy Swim
   Swim easy, taking breaks as needed.

   Saturday
   60-Minute Build Bike
   WU- 12 minutes easy
   MS- 4 x 9 minutes TP (test pace), with 2 minutes RI (recovery
   interval). Then run 5 minutes gradually building to TP.
   CD- 10 minutes easy

   Sunday
   30-Minute Easy Run
   Run/ walk easy (conversational), taking breaks as needed.

Week 4

   Monday
   Day Off
   Take the day off, including as much time off your feet as possible.
   Spend some time preparing meals for the week, as well as arranging work
   and family schedules to best allow for succesful completion of assigned
   workouts.

   Tuesday
   20-Minute Easy Swim
   Swim easy, taking breaks as needed.

   Wednesday
   Day Off

   Thursday
   45-Minute Easy Bike
   Ride easy/ conversational, and use an easy gear with a high cadence.

   Friday
   Day Off

   Saturday
   30-Minute Easy Run
   Run/walk easy (conversational), taking breaks as needed.

   Sunday
   Day Off

Week 5

   Monday
   Day Off

   Tuesday
   30-Minute Swim Test
   WU- 5 to 10 minutes easy swim
   MS- Swim 15 minutes max distance… taking breaks if/ as needed.
   CD- 5 minutes easy swim

   Wednesday
   45-Minute Easy Bike
   WU- 5 to 10 minutes easy swim
   MS- Swim 15 minutes max distance… taking breaks if/ as needed.
   CD- 5 minutes easy swim

   Thursday
   45-Minute Run Test
   WU- 10 minutes easy walk/ jog
   MS- Run/ walk 30 minutes maximum distance.
   CD- 5 minutes easy walk

   Friday
   20-Minute Easy Swim
   Swim easy, taking breaks as needed.

   Saturday
   45-Minute Bike Test
   WU- Ride 10 minutes easy
   MS- Ride 30 minutes maximum distance
   CD- Ride 5 minutes easy

   Sunday
   30-Minute Easy Run
   Run/ walk easy (conversational), taking breaks as needed.

Week 6

   Monday
   Day Off

   Tuesday
   30-Minute Build Swim
   WU- 5 minutes easy swim
   MS- 4 x 4 minutes TP (test pace), with 1 minute RI (recovery interval)
   CD- 5 minutes easy swim

   Wednesday
   45-Minute Easy Bike
   Ride easy/ conversational, and use an easy gear with a high cadence.

   Thursday
   45-Minute Build Run
   WU- 10 minutes easy walk/ jog
   MS- 4 x 5 minutes TP (test pace), with 2 minutes RI (recovery
   interval).
   CD- 8 minutes easy walk/ jog

   Friday
   20-Minute Easy Swim
   Swim easy, taking breaks as needed.

   Saturday
   60-Minute Build Bike
   WU- 12 minutes easy
   MS- 4 x 9 minutes TP (test pace), with 2 minutes RI (recovery
   interval).
   CD- 10 minutes easy

   Sunday
   30-Minute Easy Run
   Run/ walk easy (conversational), taking breaks as needed.

Week 7

   Monday
   Day Off

.
   Tuesday
   35-Minute Build Swim
   WU- 5 minutes easy swim
   MS- 4 x 5 minutes TP (test pace), with 1 minute RI (recovery interval)
   CD- 5 minutes easy swim

   Wednesday
   45-Minute Easy Bike
   Ride easy/ conversational, and use an easy gear with a high cadence.

   Thursday
   50-Minute Build Ride
   WU- 10 minutes easy walk/ jog
   MS- 4 x 6 minutes TP (test pace), with 2 minutes RI (recovery
   interval).
   CD- 8 minutes easy walk/ jog

   Friday
   20-Minute Easy Swim
   Swim easy, taking breaks as needed.

   Saturday
   65-Minute Build Bike
   WU- 12 minutes easy
   MS- 4 x 10 minutes TP (test pace), with 2 minutes RI (recovery
   interval). Then run 8 minutes gradually building to TP.
   CD- 10 minutes easy

   Sunday
   30-Minute Easy Run
   Run/ walk easy (conversational), taking breaks as needed.

Week 8

   Monday
   Day Off

   Tuesday
   20-Minute Easy Swim
   Swim easy, taking breaks as needed.

   Wednesday
   Day Off

   Thursday
   45-Minute Easy Bike
   Ride easy/conversational, and use an easy gear with a high cadence.

   Friday
   Day Off

   Saturday
   30-Minute Easy Run

   Sunday
   Day Off

Week 9

   Monday
   Day Off

   Tuesday
   30-Minute Swim Test
   WU- 5 to 10 minutes easy swim
   MS- Swim 15 minutes max distance… taking breaks if/ as needed.
   CD- 5 minutes easy swim

   Wednesday
   45-Minute Easy Bike
   Ride easy/ conversational, and use an easy gear with a high cadence.

   Thursday
   45-Minute Run Test
   WU- 10 minutes easy walk/ jog
   MS- Run/ walk 30 minutes maximum distance.
   CD- 5 minutes easy walk

   Friday
   20-Minute Easy Swim
   Swim easy, taking breaks as needed.

   Saturday
   45-Minute Bike Test
   WU- Ride 10 minutes easy
   MS- Ride 30 minutes maximum distance
   CD- Ride 5 minutes easy

   Sunday
   30-Minute Easy Run
   Run/ walk easy (conversational), taking breaks as needed.

Week 10

   Monday
   Day Off

   Tuesday
   35-Minute Build Swim
   WU- 5 minutes easy swim
   MS- 4 x 5 minutes TP (test pace), with :30 sec RI (recovery interval)
   CD- 5 minutes easy swim

   Wednesday
   45-Minute Easy Bike
   Ride easy/ conversational, and use an easy gear with a high cadence.

   Thursday
   50-Minute Build Run
   WU- 10 minutes easy walk/ jog
   MS- 4 x 6 minutes TP (test pace), with 1 minute RI (recovery interval).
   CD- 8 minutes easy walk/ jog

   Friday
   20-Minute Easy Swim
   Swim easy, taking breaks as needed.

   Saturday
   65-Minute Build Bike
   WU- 12 minutes easy
   MS- 4 x 10 minutes TP (test pace), with 1 minute RI (recovery
   interval). Then run 10 minutes gradually building to TP.
   CD- 10 minutes easy

   Sunday
   30-Minute Easy Run
   Run/ walk easy (conversational), taking breaks as needed.

Week 11

   Monday
   Day Off

   Tuesday
   25-Minute Peak Swim
   WU: 5 minutes easy
   MS: Swim 75% of goal race distance at goal race pace. Take breaks as
   needed.

   Wednesday
   45-Minute Easy Bike
   Ride easy/ conversational, and use an easy gear with a high cadence.

   Thursday
   30-Minute Peak Run
   WU- walk/ jog 5 minutes easy
   MS- Run/ walk 50% of goal race distance at goal race pace.
   CD- walk/ jog 5 minutes easy

   Friday
   20-Minute Easy Swim
   Swim easy, taking breaks as needed.

   Saturday
   45-Minute Peak Bike
   WU- 5 minutes easy spin
   MS- Bike 75% of goal race distance at goal race pace alternating 10
   minutes ‘on’, 5 minutes ‘easy’.
   CD- 5 minutes easy spin.

   Sunday
   30-Minute Easy Run
   Run/ walk easy (conversational), taking breaks as needed.

Week 12

   Monday
   Day Off

   Tuesday
   20-Minute Taper Run
   Run 33% of goal race distance at goal race pace alternating run 4
   minutes/ brisk walk 1 minute.

   Wednesday
   30-Minute Taper Bike
   Ride 50% of goal race distance at goal race pace alternating 10 minutes
   ‘on’, 5 minutes ‘easy.’

   Thursday
   15-Minute Taper Swim
   Swim 50% of goal race distance at goal race pace, taking breaks as
   needed. Practice in wetsuit if you plan to wear one in the race. Use
   the swim venue if possible, otherwise it is OK to wear the wetsuit in
   the pool.

   Friday
   Day Off

   Saturday
   20-Minute Pre-Race Workout
   Bike 15 minutes progressing to race pace, then run 5 minutes
   progressing to race pace.

   Sunday
   RACE DAY
   Arrive early, trust your sprint training plan, have fun!
"""

if __name__ == "__main__":
    parsed_data = parse_training_plan(training_plan_text)
    # Filter out entries with week 0 or other anomalies if any (though current logic shouldn't produce them)
    # Ensure all required days are present. The parser should now handle implicit Day Offs.
    
    # Correct date assignment: The first day (Monday, May 26, 2025) should be handled correctly.
    # The loop for date advancement needs to be robust.
    
    # Final check for total number of entries: 12 weeks * 7 days/week = 84 entries.
    # if len(parsed_data) != 84:
    #    print(f"Warning: Expected 84 entries, but found {len(parsed_data)}")
    #    # Optionally print week counts to debug
    #    week_counts = {}
    #    for entry in parsed_data:
    #        wk = entry['week']
    #        week_counts[wk] = week_counts.get(wk, 0) + 1
    #    print("Entries per week:", {k:v for k,v in sorted(week_counts.items())})


    with open("training_plan.json", "w") as f:
        json.dump(parsed_data, f, indent=4)
    print("Training plan parsed and saved to training_plan.json")
    if len(parsed_data) == 84:
        print("Successfully generated 84 entries.")
    else:
        print(f"Generated {len(parsed_data)} entries, expected 84.")
