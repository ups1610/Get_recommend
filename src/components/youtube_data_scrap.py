import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.logger import logging
from src.exception import CustomException
from src.utils import save_object
from dataclasses import dataclass

import sys

@dataclass
class get_data:
    data_file_path = os.path.join('artifacts','data.json')
class you_scrap:
    def __init__(self):
        self.get_data = get_data()
        self.youtube_api_key = "YOUR API"
        self.youtube = build("youtube", "v3", developerKey=self.youtube_api_key)
        logging.info("Api setup done.")

    def extract(self,query):
        try:
            # Perform the search
            logging.info("data being extracted.")
            query = query.lower()
            search_response = self.youtube.search().list(
                q=query,
                part="snippet",
                maxResults=18  # Number of results to retrieve
            ).execute() 
       
            data = {}
            number = 1
            for search_result in search_response.get("items",[]):
                # Extract the thumbnail URL, title, and video ID
                thumbnail_url = search_result["snippet"]["thumbnails"]
                if "maxres" in thumbnail_url:
                    hd_thumbnail_url = thumbnail_url["maxres"]["url"]
                else:
                    hd_thumbnail_url = thumbnail_url["high"]["url"]    
                title = search_result["snippet"]["title"]
                description = search_result["snippet"]['description']
                if 'id' in search_result and 'videoId' in search_result["id"]:
                    video_id = search_result["id"]["videoId"]  
                else:
                    video_id = '00000'    
                data[number] = {
                    "id":video_id,
                    "thumbnail_url":hd_thumbnail_url,
                    "title":title,
                    "video_id":"https://www.youtube.com/watch?v="+video_id,
                    "description":description
                }
                number+=1
            logging.info("data extrcated successfully.")   

            save_object(
                     file_path=self.get_data.data_file_path,
                     obj=data
                ) 
            return data    
                
        except Exception as e:
            raise CustomException(e,sys)

                









  