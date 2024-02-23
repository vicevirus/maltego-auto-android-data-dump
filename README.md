# Maltego Auto Mobile Dump

Maltego Auto Mobile Dump is a  Maltego transform for visualizing data extracted from mobile devices. This tool processes contacts, SMS messages, call logs, WhatsApp messages, Chrome browsing history, GPS data from images, and checks URLs against VirusTotal, providing a comprehensive overview of the data stored on a device.

Note: This project is part of GCC 2024 groupwork.

## Features

### Contacts Extraction

- **Location:** `/data/data/com.android.providers.contacts/databases/contacts2.db`
- ![Contacts Extraction GIF](images/contactDumper.gif)

### SMS Messages

- **Location:** `/data/data/com.android.providers.telephony/databases/mmssms.db`
- ![SMS Messages GIF](images/smsDumper.gif)

### Call Logs

- **Location:** `/data/data/com.android.providers.contacts/databases/calllog.db`
- ![Call Logs GIF](images/callLogDumper.gif)

### WhatsApp Messages

- **Location:** `/data/data/com.whatsapp/databases/msgstore.db`
- ![WhatsApp Messages GIF](images/whatsAppDumper.gif)

### Chrome Browsing History

- **Location:** `/data/data/com.android.chrome/app_chrome/Default/History`
- ![Chrome History GIF](images/chromeHistoryDumper.gif)

### GPS Data from Images

- **Location:** `/data/media/0/DCIM`
- ![GPS Data GIF](images/imageGPSDumper.gif)

### VirusTotal URL Analysis

- **API:** Utilizes the VirusTotal API.
- **Output:** Enriched Maltego entities with VirusTotal analysis results.
- ![VirusTotal Analysis GIF](images/virusTotalURLCheck.gif)

### Find SMS For Contacts
- ![Find SMS for contact](images/findSMSForContacts.gif)

### Find Call Logs For Contacts
- ![Find Call Logs for contact](images/findCallLogsForContact.gif)

## Note on Access Requirements

Accessing the `/data` partition on a mobile device typically requires **root access** or methods like **fastboot/JTAG**, depending on the device. These methods can bypass standard security mechanisms to retrieve data directly from the device's storage, which is essential for a comprehensive analysis. Please be aware that using these methods may void the warranty of the device and should be performed with caution.

## Usage

Use local transform. Example is available here [Maltego Local Transform Example](https://docs.maltego.com/support/solutions/articles/15000017605-local-transforms-example)

## Contributing

We welcome contributions from the community! Please read our contributing guidelines for more information on how to report issues, submit pull requests, and more.

