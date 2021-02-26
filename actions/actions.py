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
            "main building":"utter_open_close_time_main_building",
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
            "main building":"utter_open_close_time_main_building",
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

class LocationQuery(Action):
    def name(self):
        return "location_query"

    @staticmethod
    def location_utter_mapping():

        return {
            "amul":"utter_location_amul",
            "nescafe":"utter_location_nescafe",
            "nandini":"utter_location_nandini",
            "main building":"utter_location_main_building",
            "mudrika":"utter_location_printing",
            "electrical shop":"utter_location_delivery",
            "health care centre":"utter_location_health_care_centre",
            "sports complex":"utter_location_sports_complex",
            "bank":"utter_location_bank",
            "central computer centre":"utter_location_central_computer_centre",
            "central library":"utter_location_central_library",
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
            #mulitple locations or location not recognized
            dispatcher.utter_message(template="utter_default")
        
        return []
    
    def selectUtterStatment(self,location):

        location=location.lower().replace("_"," ")
        
        if location in self.location_utter_mapping().keys():
            #location recognised
            return self.location_utter_mapping()[location]
        else:
            return "utter_default"

class DepartmentQuery(Action):
    def name(self):
        return "department_query"

    @staticmethod
    def department_utter_mapping():

        return {
            "it department":"utter_location_it_department",
            "cse department":"utter_location_cse_department",
            "ece department":"utter_location_ece_department",
            "eee department":"utter_location_eee_department",
            "mech department":"utter_location_mech_department",
            "mn department":"utter_location_mn_department",
            "meta department":"utter_location_meta_department",
            "chem department":"utter_location_chem_department",
            "cv department":"utter_location_cv_department",
        }

    def run(self, dispatcher, tracker, domain):
        query_departments = []

        for e in tracker.latest_message["entities"]:
            if e["entity"]=="Department":
                query_departments.append(e["value"])
                # making a list of departments detected

        if len(query_departments)==1:
            #single department found and recognised
            department = query_departments[0]
            dispatcher.utter_message(template=self.selectUtterStatment(department))
        
        else:
            #mulitple departments or location not recognized
            dispatcher.utter_message(template="utter_default")
        
        return []
    
    def selectUtterStatment(self,department):

        department=department.lower()
        
        if department in self.department_utter_mapping().keys():
            #department recognised
            return self.department_utter_mapping()[department]
        else:
            return "utter_default"
