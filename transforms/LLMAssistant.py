# sms_transform.py
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.transform import DiscoverableTransform
from maltego_trx.entities import Phrase
import sqlite3
import os
import openai

class LLMAssistant(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request, response):
        prompt = request.Value
        prompt = request.Value
        dataDir = request.getProperty("database_path")
        try:
                message = response.addEntity(Phrase,cls.ask_llm(prompt,dataDir))
                message.addProperty(fieldName="DataDir", displayName="DataDir", value=dataDir)
        except Exception as e:
            response.addUIMessage("Failed to extract SMS: " + str(e), UIM_TYPES["partial"])

    @staticmethod
    def ask_llm(prompt, dataDir):
        openai.api_key = ""
        # Connect to the SMS database and retrieve messages
        sms_db = os.path.join(dataDir, "data", "com.android.providers.telephony", "databases", "mmssms.db")
        sms_messages = []
        try:
            conn = sqlite3.connect(sms_db)
            cursor = conn.cursor()
            cursor.execute("SELECT address, date, type, body FROM sms")
            for row in cursor.fetchall():
                address, date, type, body = row
                sms_type = "Received" if type == 1 else "Sent"
                sms_messages.append(f"From: {address}, Date: {date}, Type: {sms_type}, Message: {body}")
        except sqlite3.Error as e:
            sms_messages.append("Failed to load messages: " + str(e))
        finally:
            if conn:
                conn.close()
        
        # Combine the user's prompt with the SMS messages
        combined_prompt = f"{prompt}\n\n{' '.join(sms_messages)}"
        
        # Send the combined prompt to GPT-4
        try:
            response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an assistant to law enforcement investigators, assisting in the investigation of these messages and explaining them in detail."},{"role": "user", "content": combined_prompt}],
            max_tokens=128,
            temperature=0.5,)
            completed_text = response["choices"][0]["message"]["content"]
            return completed_text
        except Exception as e:
            return f"Failed to query OpenAI: {str(e)}"
