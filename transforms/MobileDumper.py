from maltego_trx.entities import Phrase, PhoneNumber, GPS
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.transform import DiscoverableTransform
from datetime import datetime, timedelta
import re
from transforms import ImageGPSDumper

import sqlite3
import os
import logging
# from urllib.parse import unquote
# from datetime import datetime, timedelta

logging.getLogger('PIL').setLevel(logging.WARNING)


class MobileDumper(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request, response):
        dataDir = request.Value

        # Attempt to get and process contacts
        try:
            contacts = cls.get_contacts(dataDir)
            for contact in contacts:
                person = response.addEntity("maltego.Person", contact['name'])
                person.addProperty(
                    fieldName="phonenumber", displayName="Phone Number", value=contact['phone'])
                # Use a property to indicate the category
                person.addProperty(fieldName="category",
                                   displayName="Category", value="Contacts")
        except Exception as e:
            response.addUIMessage(
                "Failed to extract contacts: " + str(e), UIM_TYPES["partial"])

        # Attempt to get and process SMS messages
        try:
            sms_messages = cls.get_sms(dataDir)
            for sms in sms_messages:
                message = response.addEntity(Phrase, sms['body'])
                message.addProperty(
                    fieldName="from", displayName="From", value=sms['address'])
                message.addProperty(
                    fieldName="date", displayName="Date", value=sms['date'])
                message.addProperty(
                    fieldName="type", displayName="Type", value=sms['type'])
                # Use a property to indicate the category
                message.addProperty(fieldName="category",
                                    displayName="Category", value="SMS")
        except Exception as e:
            response.addUIMessage(
                "Failed to extract SMS: " + str(e), UIM_TYPES["partial"])

        # Attempt to get and process call logs
        try:
            call_logs = cls.get_call_logs(dataDir)
            for call in call_logs:
                call_entity = response.addEntity(PhoneNumber, call['number'])
                call_entity.addProperty(
                    fieldName="date", displayName="Date", value=call['date'])
                call_entity.addProperty(
                    fieldName="type", displayName="Type", value=call['type'])
                call_entity.addProperty(fieldName="duration", displayName="Duration", value=str(
                    call['duration']) + " seconds")
                # Use a property to indicate the category
                call_entity.addProperty(
                    fieldName="category", displayName="Category", value="Call Logs")
        except Exception as e:
            response.addUIMessage(
                "Failed to extract call logs: " + str(e), UIM_TYPES["partial"])

        try:
            whatsapp_messages = cls.get_whatsapp_messages(dataDir)
            for msg in whatsapp_messages:
                message_entity = response.addEntity(
                    'maltego.Smartphone', msg['text_data'])
                message_entity.addProperty(
                    fieldName="timestamp", displayName="Timestamp", value=msg['timestamp'])
                message_entity.addProperty(
                    fieldName="key_id", displayName="Message ID", value=msg['key_id'])
                # Use a property to indicate the category
                message_entity.addProperty(
                    fieldName="category", displayName="Category", value="WhatsApp")
        except Exception as e:
            response.addUIMessage(
                "Failed to extract WhatsApp messages: " + str(e), UIM_TYPES["partial"])

        try:
            ImageGPSDumper.ImageGPSDumper.create_entities(request, response)
        except Exception as e:
            pass

        # # Get chrome history, but its not working rn idk why
        # try:
        #     browsing_history = cls.get_chrome_history(dataDir)
        #     for history_item in browsing_history:
        #        print(history_item)
        #        response.addEntity(Phrase, 'google.com')

        try:
            browsing_history = cls.get_chrome_history(dataDir)
            for history_item in browsing_history:
                # Truncate to prevent overly long display values
                unique_identifier = history_item['url'][:100]
                history_entity = response.addEntity(
                    'maltego.Website', unique_identifier)

                # Adding details as properties including last visited time
                history_entity.addProperty(
                    fieldName='url', displayName='URL', value=history_item['url'])
                history_entity.addProperty(
                    fieldName='last_visit_time', displayName='Last Visit Time', value=history_item['last_visit_time'])
                history_entity.addProperty(
                    fieldName='category', displayName='Category', value="Chrome History")
        except Exception as e:
            response.addUIMessage(
                "Failed to extract browsing history: " + str(e), UIM_TYPES["partial"])

    # Method for get contacts

    @staticmethod
    def get_contacts(dataDir):
        contacts_db = os.path.join(
            dataDir, "data", "com.android.providers.contacts", "databases", "contacts2.db")

        contacts = []
        try:
            conn = sqlite3.connect(contacts_db)
            cursor = conn.cursor()
            # Adapt this query based on your database schema and the information you want to extract
            cursor.execute("""
                SELECT display_name, data1 FROM raw_contacts
                JOIN data ON raw_contacts._id = data.raw_contact_id
                WHERE mimetype_id = (SELECT _id FROM mimetypes WHERE mimetype = 'vnd.android.cursor.item/phone_v2')
            """)
            for row in cursor.fetchall():
                name, phone = row
                contacts.append({'name': name, 'phone': phone})
        except sqlite3.Error as e:
            # print(f"Database error: {e}")
            pass
        finally:
            if conn:
                conn.close()
        return contacts

    # Method for get SMS

    @staticmethod
    def get_sms(dataDir):
        sms_db = os.path.join(
            dataDir, "data", "com.android.providers.telephony", "databases", "mmssms.db")
        sms = []
        try:
            conn = sqlite3.connect(sms_db)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT address, date, type, body FROM sms
            """)
            for row in cursor.fetchall():
                address, date, type, body = row
                sms_type = "Received" if type == 1 else "Sent"
                sms.append({'address': address, 'date': date,
                           'type': sms_type, 'body': body})
        except sqlite3.Error as e:
            # print(f"Database error: {e}")
            pass
        finally:
            if conn:
                conn.close()
        return sms

    # Method for get call logs

    @staticmethod
    def get_call_logs(dataDir):
        calls_db = os.path.join(dataDir, "data", "com.android.providers.contacts",
                                "databases", "calllog.db")  # Adjusted to calllog.db
        calls = []
        try:
            conn = sqlite3.connect(calls_db)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT number, date, type, duration FROM calls
            """)
            for row in cursor.fetchall():
                number, date, type_code, duration = row
                call_type = "Incoming" if type_code == 1 else "Outgoing" if type_code == 2 else "Missed"
                calls.append({'number': number, 'date': date,
                             'type': call_type, 'duration': duration})
        except sqlite3.Error as e:
            # print(f"Database error: {e}")
            pass
        finally:
            if conn:
                conn.close()
        return calls

    @staticmethod
    def get_whatsapp_messages(dataDir):
        whatsapp_db = os.path.join(
            dataDir, "data", "com.whatsapp", "databases", "msgstore.db")
        messages = []
        try:
            conn = sqlite3.connect(whatsapp_db)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT text_data, timestamp, key_id FROM message WHERE text_data IS NOT NULL
            """)
            emoji_pattern = re.compile("["
                                       u"\U0001F600-\U0001F64F"  # emoticons
                                       u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                       u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                       u"\U0001F700-\U0001F77F"  # alchemical symbols
                                       u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                                       u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                                       u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                                       u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                                       u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                                       u"\U00002702-\U000027B0"  # Dingbats
                                       u"\U000024C2-\U0001F251"
                                       "]+", flags=re.UNICODE)
            for row in cursor.fetchall():
                text_data, timestamp, key_id = row
                text_data_clean = emoji_pattern.sub(
                    r'', text_data)  # Remove emojis
                timestamp_in_seconds = timestamp / 1000  # Convert from milliseconds to seconds
                readable_time = datetime.fromtimestamp(
                    timestamp_in_seconds).strftime('%Y-%m-%d %H:%M:%S')
                messages.append({'text_data': text_data_clean,
                                'timestamp': readable_time, 'key_id': key_id})
        except sqlite3.Error as e:
            # print(f"Database error: {e}")
            pass
        finally:
            if conn:
                conn.close()
        return messages

        # Method for get chrome history
    @staticmethod
    def get_chrome_history(dataDir):
        history_db = os.path.join(dataDir, "data", "com.android.chrome",
                                  "app_chrome", "Default", "History")  # Updated path
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
                epoch_start = datetime(1601, 1, 1) + \
                    timedelta(microseconds=last_visit_time)
                readable_time = epoch_start.strftime('%Y-%m-%d %H:%M:%S')

                url_encoded = url.encode(
                    'utf-8', errors='ignore').decode('utf-8', errors='ignore')
                history.append(
                    {'url': url_encoded, 'last_visit_time': readable_time})

        except sqlite3.Error as e:
            # print(f"Database error: {e}")
            pass
        finally:
            if conn:
                conn.close()
        return history
