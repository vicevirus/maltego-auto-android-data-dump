# sms_transform.py
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.transform import DiscoverableTransform
from maltego_trx.entities import Phrase
import sqlite3
import os

class SMSDumper(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request, response):
        dataDir = request.Value
        try:
            sms_messages = cls.get_sms(dataDir)
            for sms in sms_messages:
                message = response.addEntity(Phrase, sms['body'])
                message.addProperty(fieldName="from", displayName="From", value=sms['address'])
                message.addProperty(fieldName="date", displayName="Date", value=sms['date'])
                message.addProperty(fieldName="type", displayName="Type", value=sms['type'])
                message.addProperty(fieldName="category", displayName="Category", value="SMS")
        except Exception as e:
            response.addUIMessage("Failed to extract SMS: " + str(e), UIM_TYPES["partial"])

    @staticmethod
    def get_sms(dataDir):
        sms_db = os.path.join(dataDir, "data", "com.android.providers.telephony", "databases", "mmssms.db")
        sms = []
        try:
            conn = sqlite3.connect(sms_db)
            cursor = conn.cursor()
            cursor.execute("SELECT address, date, type, body FROM sms")
            for row in cursor.fetchall():
                address, date, type, body = row
                sms_type = "Received" if type == 1 else "Sent"
                sms.append({'address': address, 'date': date, 'type': sms_type, 'body': body})
        except sqlite3.Error as e:
            pass
        finally:
            if conn:
                conn.close()
        return sms
