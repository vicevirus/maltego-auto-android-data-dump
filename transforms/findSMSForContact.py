from maltego_trx.entities import Phrase
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.transform import DiscoverableTransform
import sqlite3
import os
from datetime import datetime

class findSMSForContact(DiscoverableTransform):
    """
    A Maltego transform to find SMS messages for a given contact.
    """
    @classmethod
    def create_entities(cls, request, response):
        phone_number = request.getProperty("phonenumber")
        dataDir = request.getProperty("dataDir")
        
        sms_db = os.path.join(dataDir, "data", "com.android.providers.telephony", "databases", "mmssms.db")
        
        try:
            conn = sqlite3.connect(sms_db)
            cursor = conn.cursor()
            query = "SELECT body, date, type FROM sms WHERE address = ?"
            cursor.execute(query, (phone_number,))
            
            for row in cursor.fetchall():
                body, date, sms_type = row
                # Convert timestamp to readable format (optional)
                date_str = datetime.fromtimestamp(int(date) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                unique_body = f"{date_str}: {body}"  # Prepend the date to make each entity unique
                sms_entity = response.addEntity(Phrase, unique_body)
                sms_entity.addProperty(fieldName="date", displayName="Date", value=str(date_str))
                sms_entity.addProperty(fieldName="type", displayName="Type", value="Received" if sms_type == 1 else "Sent")
        except sqlite3.Error as e:
            response.addUIMessage(f"Failed to extract SMS: {e}", UIM_TYPES["partial"])
        finally:
            if conn:
                conn.close()
