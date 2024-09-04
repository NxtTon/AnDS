import requests
import pandas as pd
import re
import os
from app.YouTubeScraper import robo_get_video_id

class YouTubeCommentExtractor:
    

    def __init__(self, api_key, video_id=None):
        self.api_key = api_key
        self.video_id = video_id or self.get_video_id()

    def get_video_id(self):
        return robo_get_video_id()

    def fetch_comments(self):
        url = f'https://youtube.googleapis.com/youtube/v3/commentThreads?part=snippet&part=replies&videoId={self.video_id}&key={self.api_key}&alt=json'
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()

    def process_comments(self, data):
        df = pd.json_normalize(data.get('items', []))
        if 'snippet.topLevelComment.snippet.videoId' in df.columns and 'snippet.topLevelComment.snippet.textDisplay' in df.columns:
            df = df[['snippet.topLevelComment.snippet.videoId', 'snippet.topLevelComment.snippet.textDisplay']]
            df.rename(columns={
                'snippet.topLevelComment.snippet.videoId': 'video_id',
                'snippet.topLevelComment.snippet.textDisplay': 'video_comment'
            }, inplace=True)
            df['video_comment'] = df['video_comment'].apply(self._clean_comment)
            return df
        else:
            raise ValueError("As colunas esperadas não estão presentes nos dados.")

    @staticmethod
    def _clean_comment(comment):
        return re.sub(r'[^\w\s]', '', comment)

    def save_to_csv(self, df, file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        df.to_csv(file_path, index=False)
        print(f'DataFrame salvo no arquivo: {file_path}')

    def run(self, file_path):
        print("ID do vídeo:", self.video_id)
        data = self.fetch_comments()
        print("Dados brutos:", data)
        print("Estrutura dos dados:", data)
        
        df = self.process_comments(data)
        print("DataFrame final:", df)
        self.save_to_csv(df, file_path)

 
