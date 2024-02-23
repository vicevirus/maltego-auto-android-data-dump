# contacts_transform.py
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.transform import DiscoverableTransform
import sqlite3
import os

class ContactsDumper(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request, response):
        dataDir = request.Value
        try:
            contacts = cls.get_contacts(dataDir)
            for contact in contacts:
                person = response.addEntity("maltego.Person", contact['name'])
                person.addProperty(fieldName="phonenumber", displayName="Phone Number", value=contact['phone'])
                person.addProperty(fieldName="dataDir", displayName="Data Dir", value=dataDir)
                person.addProperty(fieldName="category", displayName="Category", value="Contacts")
        except Exception as e:
            response.addUIMessage("Failed to extract contacts: " + str(e), UIM_TYPES["partial"])

    @staticmethod
    def get_contacts(dataDir):
        contacts_db = os.path.join(dataDir, "data", "com.android.providers.contacts", "databases", "contacts2.db")
        contacts = []
        try:
            conn = sqlite3.connect(contacts_db)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT display_name, data1 FROM raw_contacts
                JOIN data ON raw_contacts._id = data.raw_contact_id
                WHERE mimetype_id = (SELECT _id FROM mimetypes WHERE mimetype = 'vnd.android.cursor.item/phone_v2')
            """)
            for row in cursor.fetchall():
                name, phone = row
                contacts.append({'name': name, 'phone': phone})
        except sqlite3.Error as e:
            pass
        finally:
            if conn:
                conn.close()
        return contacts
