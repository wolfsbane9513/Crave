import streamlit as st
import requests
import json
import ast
from promptify import Prompter,OpenAI, Pipeline

openai_key = ""

sentence     =  """The patient is a 93-year-old female with a medical  				 
                history of chronic right hip pain, osteoporosis,					
                hypertension, depression, and chronic atrial						
                fibrillation admitted for evaluation and management				
                of severe nausea and vomiting and urinary tract				
                infection"""

model        = OpenAI(openai_key) # or `HubModel()` for Huggingface-based inference or 'Azure' etc
prompter     = Prompter('ner.jinja') # select a template or provide custom template
pipe         = Pipeline(prompter , model)
nlp_prompter = Prompter(model)

one_shot = """5 stars to this place. Excellent food. Can be customised to your taste buds liking!! Fabulous service and attitude of staff.Self Parking is a challenge however valet takes care of your car if you are comfortable. Located in the heart of the city - KoramangalaTasty lip smacking food. They start with a garlic bread with tomato and basil spread (complimentary).
 You feel hungry when you eat this until your actual order comes. 
Soups a must try. In starters, one should try the mushroom oil fried with garlic,it was yummy. It’s delicious dish and you will want to eat it again and again. Main courses are pasta and pizza, nothing great. Overall the ambience and service of the staff is excellent. Must visit.Recently, I had the pleasure of dining at a delightful Italian restaurant that transported me straight to the heart of Italy. 
From the moment I entered, the warm and inviting atmosphere, accompanied by the aromas of freshly baked bread and simmering sauces,
 set the stage for an unforgettable culinary experience.
The ambiance of the Italian restaurant was a perfect blend of rustic charm and contemporary elegance.
The soft lighting, cozy seating arrangements, and tasteful décor created an intimate and welcoming atmosphere.
The walls adorned with vintage photographs and paintings added a touch of authenticity, 
while the soothing background music enhanced the overall dining experience. The attentive and friendly staff further elevated the ambiance,
 making me feel like a cherished guest."""
one_shot =[[one_shot,[{'E':'garlic bread','T':'DISH NAME'},{'E':'pasta','T':'DISH NAME'},{'E':'pizza','T':'DISH NAME'},{'E':'tomato and basilspread','T':'DISH NAME'},
                      {'E':'taste bud liking','T':'TASTE LEVEL'},{'E':'delicious','T':'TASTE LEVEL'}]]]
                      #{'E':'welcoming atmosphere','T':'AMBIENCE'},
                      #{'E':'cozy seating arrangements','T':'AMBIENCE'},{'E':'rustic charm','T':'AMBIENCE'},{'E':'contemporary elegance','T':'AMBIENCE'}]]]


#pprint(eval(result['text']))




# result = pipe.fit(sentence, domain="food", labels=None)


### Output

#print(result)
 
def find_restaurants(location: str, cuisine: str, budget: int):
    # Set up API key and base URL
    api_key = ''
    base_url = 'https://places.googleapis.com/v1/places:searchText'

    # Set up headers for API request
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.priceLevel,places.googleMapsUri,places.reviews,places.rating'
        #places.iconBackgroundColor, places.iconMaskBaseUri, places.location, places.photos, places.plusCode, places.types, places.utcOffsetMinutes, places.viewport, places.wheelchairAccessibleEntrance, places.internationalPhoneNumber, places.nationalPhoneNumber, places.openingHours, places.currentOpeningHours, places.secondaryOpeningHours, places.currentSecondaryOpeningHours, places.websiteUri places.curbsidePickup, places.delivery, places.dineIn, places.editorialSummary, places.priceLevel, places.rating, places.reservable, places.reviews, places.servesBeer, places.servesBreakfast, places.servesBrunch, places.servesDinner, places.servesLunch, places.servesVegetarianFood, places.servesWine, places.takeout, places.userRatingCount'
    }

    # Set up data for API request
    data = {
        'textQuery': f'{cuisine} Food in {location}'
    }

    # Make API request
    response = requests.post(base_url, headers=headers, data=json.dumps(data))
    results = response.json()['places']
    #print(results)

    # Filter results by price level
    #filtered_results = [result for result in results if result['priceLevel'] == 'PRICE_LEVEL_MODERATE' else continue]
    filtered_results = [result for result in results if 'priceLevel' in result and result['priceLevel'] == 'PRICE_LEVEL_EXPENSIVE' and result['rating'] > 4]

    # Format results
    suggestions = []
    for result in filtered_results[:3]:
        name = result['displayName']
        address = result['formattedAddress']
        maps_uri = result['googleMapsUri']
        reviews = result['reviews']
        positive_reviews = "Reviews: "
        negative_reviews = "Reviews: "
        must_try_items = []
        disliked_items = []
        ambience = []
        for review in reviews[:10]:
            if review['rating'] > 4:
                result = pipe.fit(review['originalText']['text'], domain="food items", labels = ["DISH NAME", "TASTE LEVEL","AMBIENCE"],examples=one_shot)
                print(result[0]['text'])
                text = result[0]['text'].strip('[').strip(']')
                if result[0]['text']:
                    data_list = ast.literal_eval(result[0]['text'])
                    # #data_list = json.loads(result[0]['text'])
                    # #data_list = json.loads(result[0]['text'])  # Get the inner list
                    # inner_dicts = [item for sublist in data_list for item in sublist] 
                    # print(inner_dicts)
                    data_list = data_list[0] if type(data_list) == list else list[data_list]
                    for item in data_list:
                        print(item)
                        if 'DISH NAME' in item.values():
                            must_try_items.append(item['E'])
                        if 'AMBIENCE' in item.values():
                            ambience.append(item['E'])
                positive_reviews+=review['originalText']['text']
            elif review['rating'] <= 2:
                negative_reviews+=review['originalText']['text']
                result =pipe.fit(review['originalText']['text'], domain="food items", labels = ["DISH NAME", "TASTE LEVEL","AMBIENCE"],examples=one_shot)
                if result[0]['text']:
                    data_list = ast.literal_eval(result[0]['text'])
                    #data_list = json.loads(result[0]['text'])
                    print(result[0]['text'])
                    print(data_list)
                    data_list = data_list[0] if type(data_list) == list else data_list
                    for item in data_list:
                        if 'DISH NAME' in item.values():
                            disliked_items.append(item['E'])
                        if 'AMBIENCE' in item.values():
                            ambience.append(item['E'])
            #print(must_try_items,disliked_items)
        # positive_rev = result = nlp_prompter.fit('summary.jinja',
        #                               text_input=positive_reviews,
        #                               domain="restaurant review",
        #                               token_length = None
        #                              )
        # negative_rev =result = nlp_prompter.fit('summary.jinja',
        #                               text_input=negative_reviews,
        #                               domain="restaurant review",
        #                               token_length = None
        #                              )
        # print(positive_reviews)
        # print(negative_reviews)

        suggestion = {
            'name': name,
            'address': address,
            'maps_uri': maps_uri,
            'positive_reviews': positive_reviews,
            'negative_reviews': negative_reviews,
            'must_try_items':must_try_items if must_try_items else "Not Available",
            'disliked_items': disliked_items if disliked_items else "Not Available",
            'ambience': ambience if ambience else "Not Available"
        }
        suggestions.append(suggestion)

    return suggestions


def main():
    st.title("Restaurant Finder")

    cuisine = st.text_input("Enter Cuisine:")
    budget = st.selectbox("Select Budget:", ["Low", "Medium", "High"])
    location = st.text_input("Enter Location:")

    if st.button("Find Restaurants"):
        # Call a function to fetch restaurant data based on cuisine, budget, and location
        # For demonstration purposes, let's assume 'restaurants_data' is a list of dictionaries
        restaurants_data = find_restaurants(location,cuisine,budget)
        st.subheader("Top 5 Restaurants:")

        for restaurant in restaurants_data[:5]:
            st.write("Restaurant Name:", restaurant["name"])
            st.write("Address:", restaurant["address"])
            st.write("Positive Reviews:", restaurant["positive_reviews"])
            st.write("Negative Reviews:", restaurant["negative_reviews"])
            st.write("Must Try Items:", restaurant["must_try_items"])
            st.write("Disliked Items:", restaurant["disliked_items"])
            st.write("Ambience:", restaurant["ambience"])
            st.write("--------------------------------------------------")

if __name__ == "__main__":
    main()
