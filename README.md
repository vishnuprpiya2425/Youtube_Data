YouTube Data Harvesting and Warehousing

Introduction YouTube Data Harvesting and Warehousing is a project aimed at developing a user-friendly Streamlit application that leverages the power of the Google API to extract valuable information from YouTube channels. The SQL database will be used to create tables and make them accessible for analysis and exploration within the Streamlit app.

Key Technologies and Skills

Python scripting
Data Collection
API integration
Streamlit
Data Management using SQL
Installation: To run this project, you need to install the following packages:

pip install mysql-connector-python
pip install pandas
pip install google-api-python-client
pip install streamlit
pip install requests-cache
To use this project, follow these steps:

Clone the repository: git clone https://github.com/Ragavirvk/Assignment-1
Install the required packages: pip install -r requirements.txt
Run the Streamlit app: streamlit run app.py
Access the app in your browser at http://localhost:8501
Features  Retrieve data from the YouTube API, including channel information, playlists, videos, and comments.  Store the retrieved data in a SQL database.  Analyze data using Streamlit  Perform queries on the SQL data warehouse.  Gain insights into channel performance, video metrics, and more.

Retrieving data from the YouTube API: The project utilizes the Google API to retrieve comprehensive data from YouTube channels. The data includes information on channels, playlists, videos, and comments. By interacting with the Google API, we collect the data and merge it into a JSON file.

Store the retrieved data in a SQL database: Users can choose which channel's data to migrate. To ensure compatibility with a structured format, the data is cleansed using the powerful pandas library. Following data cleaning, the information is segregated into separate tables, including channels, playlists, videos, and comments, utilizing SQL queries.

Data Analysis The project provides comprehensive data analysis capabilities using Streamlit. users can create interactive gain insights from the collected data.

Channel Analysis: Channel analysis includes insights on playlists, videos, subscribers, views, likes, comments, and durations. Gain a deep understanding of the channel's performance and audience engagement through detailed summaries.

Video Analysis: Video analysis focuses on views, likes, dislike, comments, and durations enabling both an overall channel and specific channel perspectives.

Contributing: Contributions to this project are welcome! If you encounter any issues or have suggestions for improvements, please feel free to submit a pull request.
