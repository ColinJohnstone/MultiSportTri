# Conceptual Unit Testing Guidelines for Sprint Triathlon Workout Tracker

This document outlines the conceptual unit tests that should be implemented for the Sprint Triathlon Workout Tracker to ensure its functionality and robustness. A JavaScript testing framework like Jest or Mocha, potentially with JSDOM or a browser-based tester like Cypress/Playwright, would be appropriate.

## 1. Training Data Handling & Initialization

*   **Test JSON Parsing:**
    *   Verify that the embedded `training_plan.json` data is correctly parsed when the page loads.
    *   Assert that the expected number of workout objects (84) are loaded into the JavaScript data structure.
*   **Test Date Integrity:**
    *   For a sample of workouts, verify that the `date` field has been correctly calculated and assigned, starting from May 26, 2025.
    *   Check edge cases like month transitions.
*   **Test Activity Type Integrity:**
    *   Verify that `activityType` (e.g., "Run", "Swim", "Bike", "Rest", "Test", "Brick", "Race") is correctly assigned based on the raw plan data for a sample of workouts.

## 2. Calendar Generation & Display

*   **Test Month Generation:**
    *   Verify that the calendar correctly generates the expected number of days for May, June, July, and August 2025.
    *   Ensure that days outside the current month but within the week rows are handled (e.g., shown as empty or disabled).
*   **Test Workout Population:**
    *   For a sample of dates, assert that the correct workout `title` is displayed in the corresponding calendar cell.
    *   Verify that the correct CSS classes (e.g., `.run`, `.swim`, `.bike`, `.rest`, `.test`, `.brick`, `.race-day`, `.empty`) are applied to cells based on the `activityType` from the training data.
*   **Test Handling of Pre-plan Dates:**
    *   Ensure dates in May 2025 before the plan start (May 26) are correctly marked as empty or with their original non-plan content.
*   **Test Pre-existing Races:**
    *   Verify that pre-existing races (e.g., Sporting Life 10K on May 11, Ultra Armour 10K on June 14, Toronto Marathon on Oct 19) are displayed if they don't conflict with a training plan workout.
    *   Confirm the "Toronto MultiSport Triathlon" on August 17, 2025, uses the "RACE DAY" data from the training plan.

## 3. Modal Functionality

*   **Test Modal Opening:**
    *   Simulate a click on a calendar cell with a workout.
    *   Assert that the modal becomes visible.
    *   Verify that the modal displays the correct date, workout `title` (bolded), and full `details` (preserving newlines).
*   **Test Modal for Empty Days:**
    *   Simulate a click on an empty calendar cell.
    *   Assert that the modal does not open or shows appropriate content for an empty day if designed to do so. (Current behavior: modal doesn't open for "-" content).
*   **Test Modal Close Button:**
    *   Verify the close button in the modal functions correctly.

## 4. Workout Completion Logic

*   **Test Initial Button State:**
    *   When opening the modal for an incomplete workout, assert that the completion button text is "Mark as Complete".
    *   When opening for a pre-completed workout (mocking `localStorage`), assert button text is "Mark as Incomplete".
*   **Test Toggling Completion:**
    *   Simulate clicking "Mark as Complete":
        *   Assert button text changes to "Mark as Incomplete".
        *   Assert the corresponding calendar cell receives the `.workout-complete` class.
        *   Assert `localStorage` is updated with the correct key/value.
    *   Simulate clicking "Mark as Incomplete":
        *   Assert button text changes to "Mark as Complete".
        *   Assert the calendar cell loses the `.workout-complete` class.
        *   Assert the item is removed from `localStorage`.
*   **Test Persistence:**
    *   Mock `localStorage` to have a workout marked as complete.
    *   On page load simulation, assert that the calendar cell for that workout has the `.workout-complete` class.
*   **Test Completion Button Visibility:**
    *   Assert that the completion button is hidden in the modal for "Day Off" or empty entries.

## 5. Filtering Logic (`filterEvents`)

*   **Test "Show All" Filter:**
    *   Assert that all calendar cells are visible and at full opacity.
*   **Test Type-Specific Filters (e.g., "Run"):**
    *   Activate the "Run" filter.
    *   Assert that only cells with the `.run` class (and `.empty` cells or other structural cells if they are always visible) are at full opacity. Other workout types should be faded.
    *   Ensure that completed runs still appear when the "Run" filter is active.
*   **Test "Completed" Filter:**
    *   Activate the "Completed" filter.
    *   Assert that only cells with the `.workout-complete` class are at full opacity.
*   **Test "Empty" Filter:**
    *   Activate the "Empty" filter.
    *   Assert that only cells with the `.empty` class are at full opacity.
*   **Test Filter State Management:**
    *   Verify that only one filter can be "active" at a time (visually and functionally).

## 6. Theme Toggle

*   **Test Theme Change:**
    *   Simulate a click on the theme toggle button.
    *   Assert that the `data-theme` attribute on the `<body>` changes accordingly.
*   **Test Theme Persistence:**
    *   Mock `localStorage` to have a theme preference saved.
    *   On page load simulation, assert that the `<body>` has the correct `data-theme`.

## 7. Countdown Timer

*   **Test Next Race Identification:**
    *   With a known set of race dates (predefined and from the plan), and a mocked current date:
        *   Assert that `document.getElementById('nextRaceName').textContent` displays the correct upcoming race name.
*   **Test Countdown Calculation:**
    *   Assert that `document.getElementById('countdownTime').textContent` displays the correctly calculated time difference (days, hours, minutes, seconds).
    *   Test edge cases like when a race is today or has just passed.
*   **Test "No Upcoming Races":**
    *   If all races are in the past, assert the appropriate message is shown.

## 8. Accessibility (Conceptual Checks)

*   Ensure interactive elements are keyboard accessible.
*   Colors used provide sufficient contrast (especially for text and completion indicators).
*   ARIA attributes could be considered for dynamic content changes if not already clear from context.

This conceptual outline provides a solid foundation for testing the application thoroughly.
