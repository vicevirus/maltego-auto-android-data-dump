from maltego_trx.entities import Phrase
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.transform import DiscoverableTransform
import sqlite3
import os
from datetime import datetime

class findCallLogsForContact(DiscoverableTransform):
    """
    A Maltego transform to find call logs for a given contact using LIKE query for more flexibility.
    """
    @classmethod
    def create_entities(cls, request, response):
        phone_number = request.getProperty("phonenumber")
        # Prepare the phone number for a LIKE query by adding wildcards
        like_phone_number = f"%{phone_number}%"
        dataDir = request.getProperty("dataDir")

        calls_db = os.path.join(dataDir, "data", "com.android.providers.contacts", "databases", "calllog.db")

        try:
            conn = sqlite3.connect(calls_db)
            cursor = conn.cursor()
            # Use LIKE in the query for a flexible match
            query = """
                SELECT number, date, type, duration FROM calls WHERE number LIKE ?
                """
            cursor.execute(query, (like_phone_number,))
            for row in cursor.fetchall():
                number, date, call_type, duration = row
                # Convert timestamp to readable format
                date_str = datetime.fromtimestamp(int(date) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                # Define call type
                call_type_str = "Incoming" if call_type == 1 else "Outgoing" if call_type == 2 else "Missed"
                call_details = f"{date_str} - {call_type_str} - Duration: {duration} seconds"
                # Create a unique entity for each call log
                call_log_entity = response.addEntity(Phrase, call_details)
                call_log_entity.addProperty(fieldName="date", displayName="Date", value=str(date_str))
                call_log_entity.addProperty(fieldName="type", displayName="Type", value=call_type_str)
                call_log_entity.addProperty(fieldName="duration", displayName="Duration", value=str(duration))
        except sqlite3.Error as e:
            response.addUIMessage(f"Failed to extract call logs: {e}", UIM_TYPES["partial"])
        finally:
            if conn:
                conn.close()

# Replace the following with the actual registration code for the transform
# if __name__ == '__main__':
#     FindCallLogsForContactLike.run()
