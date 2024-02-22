# call_logs_transform.py
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.transform import DiscoverableTransform
from maltego_trx.entities import PhoneNumber
import sqlite3
import os

class CallLogsDumper(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request, response):
        dataDir = request.Value
        try:
            call_logs = cls.get_call_logs(dataDir)
            for call in call_logs:
                call_entity = response.addEntity(PhoneNumber, call['number'])
                call_entity.addProperty(fieldName="date", displayName="Date", value=call['date'])
                call_entity.addProperty(fieldName="type", displayName="Type", value=call['type'])
                call_entity.addProperty(fieldName="duration", displayName="Duration", value=str(call['duration']) + " seconds")
                call_entity.addProperty(fieldName="category", displayName="Category", value="Call Logs")
        except Exception as e:
            response.addUIMessage("Failed to extract call logs: " + str(e), UIM_TYPES["partial"])

    @staticmethod
    def get_call_logs(dataDir):
        calls_db = os.path.join(dataDir, "data", "com.android.providers.contacts", "databases", "calllog.db")
        calls = []
        try:
            conn = sqlite3.connect(calls_db)
            cursor = conn.cursor()
            cursor.execute("SELECT number, date, type, duration FROM calls")
            for row in cursor.fetchall():
                number, date, type_code, duration = row
                call_type = "Incoming" if type_code == 1 else "Outgoing" if type_code == 2 else "Missed"
                calls.append({'number': number, 'date': date, 'type': call_type, 'duration': duration})
        except sqlite3.Error as e:
            pass
        finally:
            if conn:
                conn.close()
        return calls
