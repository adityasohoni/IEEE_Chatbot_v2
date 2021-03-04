# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from typing import Dict, Text, Any, List, Union

from rasa_sdk import Tracker,Action
from rasa_sdk.events import SlotSet

from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction



class ValidateRestaurantForm(FormValidationAction):
    """Example of a form validation action."""

    def name(self) -> Text:
        return "validate_restaurant_form"

    @staticmethod
    def cuisine_db() -> List[Text]:
        """Database of supported cuisines."""

        return [
            "south indian",
            "north indian",
            "continental",
            "italian",
            "punjabi",
            "mexican",
            "assamese",
        ]

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_cuisine(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""

        if value.lower() in self.cuisine_db():
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"cuisine": value}
        else:
            dispatcher.utter_message(template="utter_wrong_cuisine")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"cuisine": None}

    def validate_number_for_restaurant(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate num_people value."""

        if self.is_int(value) and int(value) > 0:
            if int(value) < 11:
                return {"number_for_restaurant": value}
            else:
                dispatcher.utter_message(template = "utter_more_num_of_people")
                return {"number_for_restaurant": None}

        else:
            dispatcher.utter_message(template="utter_wrong_num_people")
            # validation failed, set slot to None
            return {"number_for_restaurant": None}

    def validate_outdoor_seating(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate outdoor_seating value."""

        if isinstance(value, str):
            if "out" in value:
                # convert "out..." to True
                return {"outdoor_seating": True}
            elif "in" in value:
                # convert "in..." to False
                return {"outdoor_seating": False}
            else:
                dispatcher.utter_message(template="utter_wrong_outdoor_seating")
                # validation failed, set slot to None
                return {"outdoor_seating": None}

        else:
            # affirm/deny was picked up as True/False by the from_intent mapping
            return {"outdoor_seating": value}

class ActionSetSlotContextLocation(Action):
    def name(self):
        return "set_context_location"

    def run(self, dispatcher, tracker, domain):

        #setting context location as the building/landmark/shop being discussed in the conversation
        return [SlotSet("context_location", tracker.latest_message["intent"].get("name"))]

class DirectTimeQuery(Action):
    def name(self):
        return "direct_time_query"

    @staticmethod
    def location_utter_mapping():

        return {
            "amul":"utter_open_close_time_amul",
            "nescafe":"utter_open_close_time_nescafe",
            "nandini":"utter_open_close_time_nandini",
            "academic building":"utter_open_close_time_academic_building",
            "mudrika":"utter_open_close_time_printing",
            "electrical shop":"utter_open_close_time_delivery",
            "health care centre":"utter_open_close_time_health_care_centre",
            "sports complex":"utter_open_close_time_sports_complex",
            "bank":"utter_open_close_time_bank",
            "central computer centre":"utter_open_close_time_central_computer_centre",
            "central library":"utter_open_close_time_central_library",
        }

    def run(self, dispatcher, tracker, domain):
        query_locations = []

        for e in tracker.latest_message["entities"]:
            if e["entity"]=="Location":
                query_locations.append(e["value"])
                # making a list of locations detected

        if len(query_locations)==1:
            #single location found and recognised
            location = query_locations[0]
            dispatcher.utter_message(template=self.selectUtterStatment(location))
        
        else:
            #location missing or mulitple locations or location not recognized
            dispatcher.utter_message(template="utter_default")
        
        return []
    
    def selectUtterStatment(self,location):

        location=location.lower().replace("_"," ")
        
        if location in self.location_utter_mapping().keys():
            #location recognised
            return self.location_utter_mapping()[location]
        else:
            return "utter_default"
        

class IndirectTimeQuery(Action):
    
    def name(self):
        return "indirect_time_query"

    def location_utter_mapping(self):

        return {
            "snacks":"utter_open_close_time_snacks",
            "academic building":"utter_open_close_time_academic_building",
            "printing":"utter_open_close_time_printing",
            "delivery":"utter_open_close_time_delivery",
            "health care centre":"utter_open_close_time_health_care_centre",
            "sports complex":"utter_open_close_time_sports_complex",
            "bank":"utter_open_close_time_bank",
            "central computer centre":"utter_open_close_time_central_computer_centre",
            "central library":"utter_open_close_time_central_library",
        }

    def run(self, dispatcher, tracker, domain):
        
        if tracker.get_slot("context_location"):
            #some context location found
            location = tracker.get_slot("context_location")
            dispatcher.utter_message(template=self.selectUtterStatment(location))
        
        else:
            #context location missing
            dispatcher.utter_message(template="utter_default")
        
        return []

    def selectUtterStatment(self,location):

        location=location.lower().replace("_"," ")
        
        if location in self.location_utter_mapping().keys():
            #location recognised
            return self.location_utter_mapping()[location]
        else:
            return "utter_default"

class FindRestaurant(Action):
    def name(self):
        return "find_restaurant"
    
    @staticmethod
    def restaurant_db():
        """Database of restaurants."""

        return [
            {
                "name":"7th Block Night Canteen",
                "cuisine":["north indian"],
                "Outside":True,
                "Non-Veg":True
            },
            {
                "name":"NITK Block 3 Night Canteen",
                "cuisine":['continental' , 'south indian' ],
                "Outside":False,
                "Non-Veg":False
            },

            {
                "name":"NITK Food Court (OM Caterers)",
                "cuisine":["north indian","south indian"],
                "Outside":False,
                "Non-Veg":False
            },
            {
                "name":"Samudra Darshan cáfe NITK",
                "cuisine":["north indain" , "south indian"],
                "Outside":True,
                "Non-Veg":False
            },
            {
                "name":"Red Rock Residency",
                "cuisine":["north indian"],
                "Outside":True,
                "Non-Veg":True
            },
            {
                "name":"Red Rock's Bourbon Bakery & Cafe",
                "cuisine":["north indian" , "italian","continental"],
                "Outside":True,
                "Non-Veg":True
                
            },
            {
                "name":"Jyothi Prakash, Punjabi Dhaba",
                "cuisine":["Punjabi" , "north indian"],
                "Outside":True,
                "Non-Veg":True
            },
            {
                "name":"Kalash Veg Restaurant",
                "cuisine":["north indian"],
                "Outside":True,
                "Non-Veg":True
            }

        ]
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        cuisine  = tracker.get_slot('cuisine')
        number_of_seats =  tracker.get_slot('number_for_restaurant')
        outdoor_seating = tracker.get_slot('outdoor_seating')
        preferences = tracker.get_slot('preferences')
        feedback = tracker.get_slot('feedback')

        #  TODO: use above variables to find restaurant using places api
        restaurants = self.restaurant_db()
        eligible_restaurants = []


        dispatcher.utter_message(template="utter_parameters_values")
        if cuisine!=None:
            for r in restaurants:
                # print(r["cuisine"])
                if cuisine in r["cuisine"]:
                    eligible_restaurants.append(r)
            restaurants = eligible_restaurants
            eligible_restaurants = []
        if outdoor_seating!=None:
            if outdoor_seating:
                for r in restaurants:
                        if r["Outside"]:
                            eligible_restaurants.append(r)
                restaurants = eligible_restaurants   
        if len(restaurants):
            dispatcher.utter_message(template="utter_found_restaurants")
            for r in restaurants:
                dispatcher.utter_message(text = r['name'])


        events = []
        events.append(SlotSet('cuisine',None))
        events.append(SlotSet('number_for_restaurant',None))
        events.append(SlotSet('outdoor_seating',None))
        events.append(SlotSet('preferences',None))
        events.append(SlotSet('feedback',None))
        return events

class FormDetails(Action):
    def name(self):
        return "return_form_details"
 
    @staticmethod
    def cuisine_db() :
        """Database of supported cuisines."""

        return "south indian, north indian, continental, italian, punjabi, mexican and assamese"
        
    
    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]):
         cuisine  = tracker.get_slot('cuisine')
         number_of_seats =  tracker.get_slot('number_for_restaurant')
         outdoor_seating = tracker.get_slot('outdoor_seating')
         required_details = next(tracker.get_latest_entity_values('restaurant_form_details'), None)
         if required_details!=None :
             if required_details == 'cuisine':
                cuisines = self.cuisine_db() 
                dispatcher.utter_message(text = "Avaialble Cuisines are")
                dispatcher.utter_message(text = cuisines)
             if required_details == 'people':
                dispatcher.utter_message(text = "number of people can range from 1 to 10")
         else:
             if cuisine == None:
                cuisines = self.cuisine_db() 
                dispatcher.utter_message(text = "Avaialble Cuisines are")
                dispatcher.utter_message(text = cuisines)
                return []
             if number_of_seats == None:
                dispatcher.utter_message(text = "Number of people can range from 1 to 10")
                return[]
             if outdoor_seating == None:
                dispatcher.utter_message(text = "Enter Yes if u want to sit outside or no if you want to sit inside")
                return[]
         return []       

        
    
