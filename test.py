from datetime import datetime, timedelta
from dateutil import parser

def get_future_date():
    while True:
        # Prompt the user to choose a date
        user_input = input("Choose a date '2022-12-25': ")

        try:
            # Try to parse the user input as a date
            chosen_date = parser.parse(user_input)

            # Get today's date
            today_date = datetime.now()

            # Get the date 12 months from today
            max_date = today_date + timedelta(days=365)

            # Check if the chosen date is in the future
            if today_date < chosen_date <max_date:
                print(f"Chosen date: {chosen_date.strftime('%B %d, %Y')}")
                return chosen_date
            else:
                print("Please choose a date within the next 12 months.")
        except ValueError:
            print("Invalid date format. Please enter a valid date.")

# Get a future date from the user
future_date = get_future_date()

# Now you can use 'future_date' in your further processing
print("You can use the chosen future date in your code:", future_date)


a = "April 2024"