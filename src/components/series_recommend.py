import requests
from src.logger import logging
from src.exception import CustomException
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
import numpy as np
import os
import sys


class SeriesRecommend:
    def __init__(self):
        self.api = "YOUR TMDB API"
        self.df = pd.read_csv(os.path.join('data','final_series_data.csv'))

    def match_extract(self,title):
        try:
            logging.info("Requesting TMDB...")
            info_url = "https://api.themoviedb.org/3/search/tv?api_key="+self.api+"&query="+title   
            response = requests.get(info_url)
            data = response.json()
            results = data.get('results',[])
            card = {}
            num=0
            if results:
                for result in results:
                    id = result['id']
                    if  result['poster_path']:
                        image = "https://image.tmdb.org/t/p/original"+result['poster_path']
                    else:
                        image =  "/static/images/movie_placeholder.jpeg" 
                    if 'name' in result :     
                        name = str(result['name'])
                    else:
                        name = str(result['original_name'])
                    if  'vote_average' in result:
                        rating = str(result['vote_average'])
                    else:
                        rating = "NA"
                    card[num] = {
                        'id':id,
                        'image':image,
                        'name':name,
                        'rating':rating
                    }
                    num = num+1
            logging.info("TMDB extracted successfully")        
            return card        

        except Exception as e:
            logging.info("Exception occured in match_extract function.")
            raise CustomException(e,sys)

    def year_info(self,year):
        try:
            logging.info("Year Based Extraction initiated..")
            start_year = float(year.split(' ')[1])
            end_year = float(year.split(' ')[0])
            df = self.df[(self.df['year']>=start_year) & (self.df['year']<=end_year)]
            random_state = np.random.randint(1,50)
            new_df = df.sample(n=min(6,len(df)-1),random_state=random_state)
            titles = list(new_df['title'])
            card = {}
            num = 101
            for title in titles:
                data = self.match_extract(title)
                if len(data)>=1:
                    id = data[0]['id']
                    name = data[0]['name']
                    rating = data[0]['rating']
                    image = data[0]['image']
                    card[num] = {
                        'id':id,
                        'name':name,
                        'image':image,
                        'rating':rating
                    }
                    num = num+1
                else:
                    num = num+1
                    continue
            return card
        except Exception as e:
            logging.info("Error occured in year_info function.")
            raise CustomException(e,sys) 

    def genre_info(self,genre):
        try:
            logging.info("Genre Based Extraction initiated..")
            df = self.df[self.df['genre']==genre]
            random_state = np.random.randint(1,50)
            new_df = df.sample(n=min(6,len(df)-1),random_state=random_state)
            titles = list(new_df['title'])
            card = {}
            num = 101
            for title in titles:
                data = self.match_extract(title)
                if len(data)>=1:
                    id = data[0]['id']
                    name = data[0]['name']
                    rating = data[0]['rating']
                    image = data[0]['image']
                    card[num] = {
                        'id':id,
                        'name':name,
                        'image':image,
                        'rating':rating
                    }
                    num = num+1
                else:
                    num = num+1
                    continue
            return card
        except Exception as e:
            logging.info("Error occured in genre_info function.")
            raise CustomException(e,sys) 
    
    def rating_info(self,rating):
        try:
            logging.info("Rating Based Extraction initiated..")
            rate = float(rating)
            if(rate==10.0):
                df = self.df[self.df['rating']==rate]
            else:    
                df = self.df[(self.df['rating']>=rate) & (self.df['rating']<(rate+1.0))]
            random_state = np.random.randint(1,50)
            new_df = df.sample(n=min(6,len(df)-1),random_state=random_state)
            titles = list(new_df['title'])
            card = {}
            num = 101
            for title in titles:
                data = self.match_extract(title)
                if len(data)>=1:
                    id = data[0]['id']
                    name = data[0]['name']
                    rating = data[0]['rating']
                    image = data[0]['image']
                    card[num] = {
                        'id':id,
                        'name':name,
                        'image':image,
                        'rating':rating
                    }
                    num = num+1
                else:
                    num = num+1
                    continue
            return card
        except Exception as e:
            logging.info("Error occured in rating_info function.")
            raise CustomException(e,sys) 

    def click_info(self,id):
        try:
            logging.info("Requesting TMDB...")
            info_url = "https://api.themoviedb.org/3/tv/"+id+"?api_key=00efec2804c4bb80cc77673e690051af"
            response = requests.get(info_url)
            data = response.json()
            card = {}
            num = 101
            
            name = data['name']
            if data['poster_path']:
                image = "https://image.tmdb.org/t/p/original"+data['poster_path']
            else:
                image =  "/static/images/movie_placeholder.jpeg"     
            genre = {}
            index = 0
            for type in data['genres']:
                genre[index] = type['name']
                index = index + 1
            if data['vote_average']:    
               rating = str(data['vote_average'])[0:3] 
            else:
                rating = "NA"   
            if data['overview']:     
                overview = data['overview']
            else:
                overview = "NA"  
            if data['first_air_date']:       
               first_air_date = data['first_air_date']
            else:
                first_air_date = "NA"  
            if data['last_air_date']:      
                last_air_date = data['last_air_date']
            else:
                last_air_date = "NA" 
            if data['number_of_seasons']:       
                seasons = data['number_of_seasons']
            else:
                seasons = "NA"  
            if  data['number_of_episodes']:     
                episodes = data['number_of_episodes']
            else:
                episodes = "NA"
            if  data['episode_run_time'] :
                runtime = data['episode_run_time'] 
            else:
                runtime = "NA"
            if  data['status']:       
                status = data['status']
            else:
                status = "NA"
            if  data['spoken_languages']:       
                language = data['spoken_languages'][0]['name']
            else:
                language = data['original_language']    
            card[num]={
                'id':id,
                'name':name,
                'image':image,
                'genre':genre,
                'overview':overview,
                'rating':rating,
                'first_air_date':first_air_date,
                'last_air_date':last_air_date,
                'seasons':seasons,
                'episodes':episodes,
                'runtime':runtime,
                'status':status,
                'ln':language
            }
            return card    

        except Exception as e:
            logging.info("Exception occured in click_info function.")
            raise CustomException(e,sys)    

        
    def model_creation(self):
        try:
            logging.info("Model creation initiated..")
            tfv = TfidfVectorizer()
            tfv_matrix = tfv.fit_transform(self.df['comb'].head(20000))
            print(tfv_matrix.shape)
            # Compute the cosine similarity matrix
            cosine_sim = linear_kernel(tfv_matrix, tfv_matrix)
            print(type(cosine_sim))
            np.save(os.path.join('artifacts','recommend.npy'),cosine_sim)
            logging.info("Model Created successfully.")
        except Exception as e:
            logging.info("Error occured in series_model_creation function") 

    def series_recommend(self,title):
        try:
            cosine_sim = np.load(os.path.join('artifacts','recommend.npy'))
            #reverse mapping
            indices = pd.Series(self.df.index, index=self.df['title']).drop_duplicates()
            # Function that takes in movie title as input and outputs most similar movies
            def get_recommendations(title=title, cosine_sim=cosine_sim):
                idx = indices[title]
                # Get the pairwsie similarity scores of all movies with that movie
                sim_scores = list(enumerate(cosine_sim[idx]))
                # Sort the movies based on the similarity scores
                sim_scores = sorted(sim_scores, key=lambda x: x[1].all(), reverse=True)
                sim_scores = sim_scores[1:11]
                movie_indices = [i[0] for i in sim_scores]
                return self.df['title'].iloc[movie_indices]
            recommended_data = get_recommendations('college romance').tolist()
            return recommended_data
        except Exception as e:
            logging.info("Error occured in series_recommend function") 
            raise CustomException(e,sys)            
    
    # def recommendData_extract(self,data):
    #     try:
    #         card = {}
    #         if len(data)<3:
    #            num = 0
    #            for title in data:    
    #                 info = self.match_extract(title)
    #                 if len(info)>0:
    #                     for _,item in info.items():
    #                         card[num] = {
    #                             'image':item['image'],
    #                             'title':item['title'],
    #                             'rating':item['rating']
    #                         }
    #                         num = num + 1
    #                 else:
    #                     continue
    #         else:
    #             num = 0
    #             card = {}
    #             for title in data:
    #                 info = self.match_extract(title)
    #                 if len(info)>0:
    #                     for _,item in info.items():
    #                         card[num] = {
    #                             'image':item['image'],
    #                             'name':item['name'],
    #                             'rating':item['rating']
    #                         }
    #                         break
    #                     num = num + 1
    #                 else:
    #                     continue    
    #         return card
    #     except Exception as e:
    #         logging.info("Error occured in recommendData function.")
    
    #         raise CustomException(e,sys)

    def getRecommendSeries(self,id):
        try:
            logging.info('Request TMDB...')
            info_url = "https://api.themoviedb.org/3/tv/"+id+"/recommendations?api_key="+self.api
            response = requests.get(info_url)
            data = response.json()
            results = data.get('results',[])
            num = 0
            card = {}
            for result in results:
                id_no = result['id'] 
                if 'poster_path' in result:
                    image = "https://image.tmdb.org/t/p/original"+result['poster_path']
                else:
                    image =  "/static/images/movie_placeholder.jpeg" 
                if 'name' in result :     
                    name = str(result['name'])
                else:
                    name = str(result['original_name'])
                if  'vote_average' in result:
                    rating = str(result['vote_average'])
                else:
                    rating = "NA"
                card[num] = {
                    'id':id_no,
                    'image':image,
                    'name':name,
                    'rating':rating
                }
                num = num+1
            return card
        except Exception as e:
            logging.info("Error occured in getRecommendSeries")
            raise CustomException(e,sys)              

if __name__ == "__main__":
    obj = SeriesRecommend()
    print(obj.getRecommendSeries('100911'))
    