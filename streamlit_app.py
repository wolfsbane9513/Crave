import requests

# Define the base URL for the Google Places API
base_url = "https://places.googleapis.com/v1/places:searchText"

# Define the API key for authentication
api_key = ""



# Define a function to get the restaurants with reviews
# Import the requests library to make HTTP requests
# Define a function to get the restaurants with reviews
def get_restaurants(location, distance, cuisine, budget):
  # Convert the distance from meters to kilometers
  distance = distance / 1000

  # Create a dictionary to store the parameters for the API request
  params = {
    "key": api_key, # The API key
    "input": location, # The name of the location
    "inputtype": "textquery", # The type of input
    "fields": "name,formatted_address,geometry,rating,user_ratings_total" # The fields to return
  }

  # Make a request to the Find Place API to get the place ID of the location
  response = requests.get(base_url + "findplacefromtext/json", params=params)
  print(response.status_code)
  # Check if the request was successful
  if response.status_code == 200:
    # Parse the JSON response
    data = response.json()

    # Check if any candidates were found
    if data["status"] == "OK" and data["candidates"]:
      # Get the first candidate's place ID
      place_id = data["candidates"][0]["place_id"]

      # Create a dictionary to store the parameters for the API request
      params = {
        "key": api_key, # The API key
        "locationbias": f"circle:{distance}@{place_id}", # The location bias based on the place ID and distance
        "type": "restaurant", # The type of place
        "keyword": cuisine, # The keyword to filter by cuisine
        "maxprice": budget # The maximum price level to filter by budget (added this line)
      }

      # Make a request to the Nearby Search API to get the restaurants near the location
      response = requests.get(base_url + "nearbysearch/json", params=params)
      print(response.status_code)
      # Check if the request was successful
      if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Check if any results were found
        if data["status"] == "OK" and data["results"]:
          # Loop through the results
          for result in data["results"]:
            # Print the name and address of the restaurant
            print(result["name"])
            print(result["vicinity"])

            # Get the place ID of the restaurant
            place_id = result["place_id"]

            # Create a dictionary to store the parameters for the API request
            params = {
              "key": api_key, # The API key
              "place_id": place_id, # The place ID of the restaurant
              "fields": "review,website,opening_hours" # The fields to return (added opening_hours)
            }

            # Make a request to the Place Details API to get the reviews, website and opening hours of the restaurant
            response = requests.get(base_url + "details/json", params=params)

            # Check if the request was successful
            if response.status_code == 200:
              # Parse the JSON response
              data = response.json()

              # Check if any reviews were found
              if data["status"] == "OK" and data["result"]["reviews"]:
                # Print a separator line
                print("-" * 40)

                # Print the website URL of the restaurant 
                print(data["result"]["website"])

                # Print the opening hours of the restaurant (added this line)
                print(data["result"]["opening_hours"]["weekday_text"])

                # Loop through the reviews
                for review in data["result"]["reviews"]:
                  # Print the author name and rating of the review
                  print(review["author_name"], review["rating"])

                  # Print the text of the review
                  print(review["text"])

                  # Print a separator line
                  print("-" * 40)
                
                # Print an empty line for spacing
                print()

get_restaurants("mahadeva pura, bangalore",10000,"chinese","2000")