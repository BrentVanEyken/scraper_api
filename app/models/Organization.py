import requests

from .. import scraper
from . import Website

from enum import Enum

class UpdateMethods(Enum):
    MANUAL = "manual"
    AUTO = "auto"

class Organization:
    def __init__(self, name, address, email, phone_number, website, latitude, longitude, main_contact, category, hours, description, update_method=UpdateMethods.MANUAL):
        self.name = name
        self.address = address
        self.email = email
        self.phone_number = phone_number
        self.website = website
        self.latitude = latitude
        self.longitude = longitude
        self.main_contact = main_contact
        self.category = category
        self.hours = hours
        self.description = description

        self.update_method=update_method

#Getters
#==================================================================

    def get_name(self):
        return self.name

    def get_address(self):
        return self.address

    def get_email(self):
        return self.email

    def get_phone_number(self):
        return self.phone_number

    def get_website(self):
        return self.website

    def get_latitude(self):
        return self.latitude

    def get_longitude(self):
        return self.longitude

    def get_main_contact(self):
        return self.main_contact

    def get_category(self):
        return self.category

    def get_hours(self):
        return self.hours

    def get_description(self):
        return self.description
    
    
    def get_update_method(self):
        return self.update_method

#Setters
#==================================================================

    def set_name(self, name):
        self.name = name

    def set_address(self, address):
        self.address = address

    def set_email(self, email):
        self.email = email

    def set_phone_number(self, phone_number):
        self.phone_number = phone_number

    def set_website(self, website):
        self.website = website

    def set_latitude(self, latitude):
        self.latitude = latitude

    def set_longitude(self, longitude):
        self.longitude = longitude

    def set_main_contact(self, main_contact):
        self.main_contact = main_contact

    def set_category(self, category):
        self.category = category

    def set_hours(self, hours):
        self.hours = hours

    def set_description(self, description):
        self.description = description

    
    def set_update_method(self, update_method:UpdateMethods):
        self.update_method = update_method


#Custom methods
#==================================================================

    def setCoordinates(self,address):
        try:
            response = requests.get(f"https://nominatim.openstreetmap.org/search?format=json&q={address}")
            data = response.json()
            if data and len(data) > 0:
                self.latitude=data[0]['lat']
                self.longitude=data[0]['lon']
        except Exception as error:
            print(f"Error converting address to coördinates: {error}")
            self.latitude=None
            self.longitude=None

#magic methods
#==================================================================

    def __str__(self):
        return (
            f"Organization: {self.name}\n"
            f"Address: {self.address}\n"
            f"Email: {self.email}\n"
            f"Phone Number: {self.phone_number}\n"
            f"Website: {self.website}\n"
            f"Location: ({self.latitude}, {self.longitude})\n"
            f"Main Contact: {self.main_contact}\n"
            f"Category: {self.category}\n"
            f"Hours: {self.hours}\n"
            f"Description: {self.description}\n"
        )
    
#Class methods
#==================================================================

    @classmethod
    def getCoordinates(cls, address:str):
        """
            Returns a tuple containging the latitude and longitude associated with the provided address (lat,long)
        """
        lat=None
        long=None
        try:
            response = requests.get(f"https://nominatim.openstreetmap.org/search?format=json&q={address}")
            data = response.json()
            if data and len(data) > 0:
                lat=data[0]['lat']
                long=data[0]['lon']
        except Exception as error:
            print(f"Error converting address to coördinates: {error}")
        
        return (lat,long)

    @classmethod
    def from_website(cls, website:Website):
        """
        Creates an Organization object by scraping the content from a Website object.
        
        Args:
            website (Website): The Website object containing URLs and element IDs.

        Returns:
            Organization: The scraped Organization object.
        """
        # Use the scrape_content method to extract information for each attribute
        name = scraper.scrape_content(website.get_name_url(), website.get_name_id())
        address = scraper.scrape_content(website.get_address_url(), website.get_address_id())
        email = scraper.scrape_content(website.get_email_url(), website.get_email_id())
        phone_number = scraper.scrape_content(website.get_phone_number_url(), website.get_phone_number_id())
        website_link = website.get_website_url()
        main_contact = scraper.scrape_content(website.get_main_contact_url(), website.get_main_contact_id())
        category = scraper.scrape_content(website.get_category_url(), website.get_category_id())
        hours = scraper.scrape_content(website.get_hours_url(), website.get_hours_id())
        description = scraper.scrape_content(website.get_description_url(), website.get_description_id())

        coordinates = cls.getCoordinates(address)

        latitude = coordinates[0]
        longitude = coordinates[1]

        # Create and return an Organization object using the scraped data
        return cls(
            name=name,
            address=address,
            email=email,
            phone_number=phone_number,
            website=website_link,
            latitude=latitude,
            longitude=longitude,
            main_contact=main_contact,
            category=category,
            hours=hours,
            description=description,
            update_method=UpdateMethods.AUTO
        )