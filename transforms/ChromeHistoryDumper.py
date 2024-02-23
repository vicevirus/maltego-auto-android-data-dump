from maltego_trx.entities import Website
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.transform import DiscoverableTransform
from datetime import datetime, timedelta
import sqlite3
import os

class ChromeHistoryDumper(DiscoverableTransform):
    """
    A Maltego transform to extract and present Chrome browsing history.
    """
    @classmethod
    def create_entities(cls, request, response):
        dataDir = request.Value

        try:
            browsing_history = cls.get_chrome_history(dataDir)
            for history_item in browsing_history:
                # Truncate URL to prevent overly long display values, if necessary
                unique_identifier = history_item['url'][:100]  
                history_entity = response.addEntity(Website, unique_identifier)

                # Adding details as properties including last visited time
                history_entity.addProperty(fieldName='url', displayName='URL', value=history_item['url'])
                history_entity.addProperty(fieldName='last_visit_time', displayName='Last Visit Time', value=history_item['last_visit_time'])
                history_entity.addProperty(fieldName='category', displayName='Category', value="Chrome History")
        except Exception as e:
            response.addUIMessage("Failed to extract browsing history: " + str(e), UIM_TYPES["partial"])

    @staticmethod
    def get_chrome_history(dataDir):
        history_db = os.path.join(dataDir, "data", "com.android.chrome", "app_chrome", "Default", "History")
        history = []
        try:
            conn = sqlite3.connect(history_db)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT url, last_visit_time FROM urls WHERE hidden = 0 ORDER BY last_visit_time DESC
            """)
            for row in cursor.fetchall():
                url, last_visit_time = row
                # Convert last_visit_time from microseconds since January 1, 1601, to a readable datetime format
                epoch_start = datetime(1601, 1, 1) + timedelta(microseconds=last_visit_time)
                readable_time = epoch_start.strftime('%Y-%m-%d %H:%M:%S')

                url_encoded = url.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
                history.append({'url': url_encoded, 'last_visit_time': readable_time})
        except sqlite3.Error as e:
            pass  # Handle or log the error as needed
        finally:
            if conn:
                conn.close()
        return history
        