from maltego_trx.entities import URL
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.transform import DiscoverableTransform
import requests
import time

# Your VirusTotal API key
VIRUSTOTAL_API_KEY = '397e1fd56d7dae7199726a6e8f951d9527d9c90842e595e89aeb643f7adfc08a'

class VirusTotalURLCheck(DiscoverableTransform):
    """
    A Maltego transform to submit a URL to VirusTotal, retrieve analysis results,
    and display the statistics as properties in Maltego.
    """
    @classmethod
    def create_entities(cls, request, response):
        url_to_analyze = request.Value
        headers = {"x-apikey": VIRUSTOTAL_API_KEY}

        # Submit the URL for analysis
        submit_response = requests.post("https://www.virustotal.com/api/v3/urls",
                                        headers=headers,
                                        data={"url": url_to_analyze})
    
        if submit_response.status_code == 200:
            submit_result = submit_response.json()
            analysis_id = submit_result["data"]["id"]



            # Retrieve the analysis results
            analysis_response = requests.get(f"https://www.virustotal.com/api/v3/analyses/{analysis_id}", headers=headers)
            if analysis_response.status_code == 200:
                analysis_result = analysis_response.json()
                stats = analysis_result["data"]["attributes"]["stats"]

                # Create the URL entity and add statistics as properties
                url_entity = response.addEntity('maltego.CrimeScene', f"{url_to_analyze} Virustotal Analysis")
                for stat, value in stats.items():
                    url_entity.addProperty(fieldName=stat, displayName=stat.capitalize(), value=str(value))
                response.addUIMessage("Analysis completed successfully.", messageType=UIM_TYPES["inform"])
            else:
                response.addUIMessage("Failed to retrieve analysis results.", messageType=UIM_TYPES["partial"])
        else:
            response.addUIMessage("Failed to submit URL for analysis.", messageType=UIM_TYPES["partial"])


