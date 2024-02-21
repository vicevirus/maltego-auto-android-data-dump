from maltego_trx.entities import Person
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.transform import DiscoverableTransform
import requests

class VerifyPhoneNumber(DiscoverableTransform):
    """
    A Maltego transform to verify a phone number using the Veriphone API.
    """

    @classmethod
    def create_entities(cls, request, response):
        # Extract phone number from the incoming entity
        phone_number = request.getProperty("phonenumber")
        api_key = "A6B736FF3071406FAFB81D647C99ED99"

        if not api_key:
            response.addUIMessage("API key for Veriphone is not set.", UIM_TYPES["partial"])
            return

        # Prepare the API request
        api_url = "https://api.veriphone.io/v2/verify"
        params = {
            "phone": phone_number,
            "key": api_key
        }

        try:
            # Make the API call
            api_response = requests.get(api_url, params=params)
            api_response.raise_for_status()  # Raise an error for bad responses
            data = api_response.json()

            if data.get("phone_valid"):
                # Create a new entity for the phone region
                cls.add_phone_region_entity(response, data)
            else:
                response.addUIMessage("Phone number validation failed or phone number is invalid.", UIM_TYPES["partial"])
        except Exception as e:
            response.addUIMessage(f"Failed to call Veriphone API: {str(e)}", UIM_TYPES["partial"])

    @classmethod
    def add_phone_region_entity(cls, response, data):
        """
        Adds a phone region entity to the response based on API data.
        """
        phone_region = response.addEntity("maltego.Location", data.get("phone_region"))
        # Adding more properties to the entity as needed
        phone_region.addProperty(fieldName="country", displayName="Country", value=data.get("country"))
        phone_region.addProperty(fieldName="carrier", displayName="Carrier", value=data.get("carrier"))
        # You can add more properties here as needed

# Boilerplate code to ensure the transform script can run stand-alone or be imported
if __name__ == "__main__":
    VerifyPhoneNumber.run_transform()


