class Website:
    def __init__(self, name, address, email, phone_number, website_url, main_contact, category, hours, description):
        # Each attribute is a tuple: (URL, objectID) 
        # except for website_url which is the root website url in the form of a string
        self.name = name  # Example: ("https://example.com/organization", "#org_name")
        self.address = address
        self.email = email
        self.phone_number = phone_number
        self.website_url = website_url #https://example.com/
        self.main_contact = main_contact
        self.category = category
        self.hours = hours
        self.description = description

#Getters
#==================================================================

    def get_name_url(self):
        return self.name[0]

    def get_name_id(self):
        return self.name[1]

    def get_address_url(self):
        return self.address[0]

    def get_address_id(self):
        return self.address[1]

    def get_email_url(self):
        return self.email[0]

    def get_email_id(self):
        return self.email[1]

    def get_phone_number_url(self):
        return self.phone_number[0]

    def get_phone_number_id(self):
        return self.phone_number[1]

    def get_website_url(self):
        return self.website_url

    def get_main_contact_url(self):
        return self.main_contact[0]

    def get_main_contact_id(self):
        return self.main_contact[1]

    def get_category_url(self):
        return self.category[0]

    def get_category_id(self):
        return self.category[1]

    def get_hours_url(self):
        return self.hours[0]

    def get_hours_id(self):
        return self.hours[1]

    def get_description_url(self):
        return self.description[0]

    def get_description_id(self):
        return self.description[1]

#Setters
#==================================================================

    def set_name_url(self, url):
        self.name = (url, self.name[1])

    def set_name_id(self, css_id):
        self.name = (self.name[0], css_id)

    def set_address_url(self, url):
        self.address = (url, self.address[1])

    def set_address_id(self, css_id):
        self.address = (self.address[0], css_id)

    def set_email_url(self, url):
        self.email = (url, self.email[1])

    def set_email_id(self, css_id):
        self.email = (self.email[0], css_id)

    def set_phone_number_url(self, url):
        self.phone_number = (url, self.phone_number[1])

    def set_phone_number_id(self, css_id):
        self.phone_number = (self.phone_number[0], css_id)

    def set_website_url(self, url):
        self.website = url

    def set_main_contact_url(self, url):
        self.main_contact = (url, self.main_contact[1])

    def set_main_contact_id(self, css_id):
        self.main_contact = (self.main_contact[0], css_id)

    def set_category_url(self, url):
        self.category = (url, self.category[1])

    def set_category_id(self, css_id):
        self.category = (self.category[0], css_id)

    def set_hours_url(self, url):
        self.hours = (url, self.hours[1])

    def set_hours_id(self, css_id):
        self.hours = (self.hours[0], css_id)

    def set_description_url(self, url):
        self.description = (url, self.description[1])

    def set_description_id(self, css_id):
        self.description = (self.description[0], css_id)

#Magic methods
#==================================================================

    def __str__(self):
        return (
            f"Website Configuration:\n"
            f"Name: {self.name}\n"
            f"Address: {self.address}\n"
            f"Email: {self.email}\n"
            f"Phone Number: {self.phone_number}\n"
            f"Website: {self.website_url}\n"
            f"Main Contact: {self.main_contact}\n"
            f"Category: {self.category}\n"
            f"Hours: {self.hours}\n"
            f"Description: {self.description}\n"
        )

