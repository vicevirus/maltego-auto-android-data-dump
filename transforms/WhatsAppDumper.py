# whatsapp_transform.py
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.transform import DiscoverableTransform
import sqlite3
import os
import re
from datetime import datetime

class WhatsAppDumper(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request, response):
        dataDir = request.Value
        try:
            whatsapp_messages = cls.get_whatsapp_messages(dataDir)
            for msg in whatsapp_messages:
                message_entity = response.addEntity('maltego.Smartphone', msg['text_data'])
                message_entity.addProperty(fieldName="timestamp", displayName="Timestamp", value=msg['timestamp'])
                message_entity.addProperty(fieldName="key_id", displayName="Message ID", value=msg['key_id'])
                message_entity.addProperty(fieldName="category", displayName="Category", value="WhatsApp")
        except Exception as e:
            response.addUIMessage("Failed to extract WhatsApp messages: " + str(e), UIM_TYPES["partial"])

    @staticmethod
    def get_whatsapp_messages(dataDir):
        whatsapp_db = os.path.join(dataDir, "data", "com.whatsapp", "databases", "msgstore.db")
        messages = []
        try:
            conn = sqlite3.connect(whatsapp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT text_data, timestamp, key_id FROM message WHERE text_data IS NOT NULL")
            emoji_pattern = re.compile("["
                                       u"\U0001F600-\U0001F64F"
                                       u"\U0001F300-\U0001F5FF"
                                       u"\U0001F680-\U0001F6FF"
                                       u"\U0001F700-\U0001F77F"
                                       u"\U0001F780-\U0001F7FF"
                                       u"\U0001F800-\U0001F8FF"
                                       u"\U0001F900-\U0001F9FF"
                                       u"\U0001FA00-\U0001FA6F"
                                       u"\U0001FA70-\U0001FAFF"
                                       u"\U00002702-\U000027B0"
                                       u"\U000024C2-\U0001F251"
                                       "]+", flags=re.UNICODE)
            for row in cursor.fetchall():
                text_data, timestamp, key_id = row
                text_data_clean = emoji_pattern.sub(r'', text_data)  # Remove emojis
                timestamp_in_seconds = timestamp / 1000  # Convert to seconds
                readable_time = datetime.fromtimestamp(timestamp_in_seconds).strftime('%Y-%m-%d %H:%M:%S')
                messages.append({'text_data': text_data_clean, 'timestamp': readable_time, 'key_id': key_id})
        except sqlite3.Error as e:
            pass
        finally:
            if conn:
                conn.close()
        return messages
