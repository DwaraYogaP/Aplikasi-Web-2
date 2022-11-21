import streamlit as st
import pandas as pd
import tweepy

import re
from textblob import TextBlob

@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')


CONSUMER_KEY = "QpD5DHvxnpQ9s4JAyilQO3VNj"
CONSUMER_SECRET = "xR1lzr4KrBdCcbPdpJGMwBbvfWIYMZX3r8kXcylS6dOIRqJ5fc"
ACCESS_TOKEN = "1581851324941217793-L3OYtFnQIqkCUcG2xerHf1xeN2JOyL"
ACCESS_TOKEN_SECRET = "j4bbLWEKfQAYkxJxodTSZyjPlFpTeu3Da7llp9YVbZKFZ"
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

menu = ["Crawling Data", "Sentiment Analysis"]
choice = st.sidebar.selectbox("Menu",menu)

#Crawling Data
if choice == 'Crawling Data':
    st.title("Crawling Data Twitter")
    tab1, tab2 = st.tabs(["Keyword", "Username"])
    with tab1 :
        text = st.text_area("Masukkan Text")
        limit = st.slider("Jumlah tweet", 10, 500)
        if st.button("Cari"):
            st.text("Hasil Pencarian :")
            if text == '':
                st.warning("Silahkan masukkan teks terlebih dahulu!")
            else:
                data = api.search_tweets(q=text, lang="id", count=limit)
                json_data = [r._json for r in data]

                df = pd.json_normalize(json_data)

                st.write(df[['created_at', 'user.name', 'user.screen_name', 'text']])

                csv = convert_df(df[['created_at', 'user.name', 'user.screen_name', 'text']])

                st.download_button(
                    label="Download data",
                    data=csv,
                    file_name='data.csv',
                    mime='text/csv',
                )
    with tab2 :
        user = st.text_input("Masukkan Nama Pengguna")
        user_limit = st.slider("Jumlah tweet", 10, 500, key=2)
        
        if st.button("Cari", key=1):
            tweets = api.user_timeline(screen_name=user, count=user_limit)
            user_search =[]
            for teks in tweets:
                teks_properties= {}
                teks_properties["Tanggal"]=teks.created_at
                # teks_properties["Pengguna"]=teks.user.screen_name
                teks_properties["Tweet"]= teks.text

                if teks.retweet_count > 0:
                    if teks_properties not in user_search:
                        user_search.append(teks_properties)
                else:
                    user_search.append(teks_properties)
            
            df_user = pd.DataFrame(user_search)
            st.dataframe(df_user)

#Sentiment Analysis Twitter
if choice == 'Sentiment Analysis' :
    st.title("Sentiment Analysis Twitter")
    text = st.text_input("Masukkan teks")
    limit = st.slider("Jumlah tweet", 10, 500)
    if st.button("Analyze"):
        if text == '':
            st.warning("Silahkan masukkan teks!")
        else:
            search = api.search_tweets(q=text, lang="id", count=limit, tweet_mode="extended")

            data_search =[]
            for teks in search:
                teks_properties= {}
                teks_properties["Tanggal"]=teks.created_at
                teks_properties["Pengguna"]=teks.user.screen_name
                teks_clean = ' '.join(re.sub("(@[A-Za-z0-9]+)"," ",teks.full_text).split())
                teks_properties["Tweet"]= teks_clean

                analysis = TextBlob(teks_clean)
                if analysis.sentiment.polarity > 0.0:
                    teks_properties["Sentimen"]= 'Positif'
                elif analysis.sentiment.polarity == 0.0:
                    teks_properties["Sentimen"]= 'Netral'
                else:
                    teks_properties["Sentimen"]= 'Negatif'

                if teks.retweet_count > 0:
                    if teks_properties not in data_search:
                        data_search.append(teks_properties)
                else:
                    data_search.append(teks_properties)

            df = pd.DataFrame(data_search)

            csv = convert_df(df[["Sentimen", "Pengguna", "Tweet", "Tanggal"]])
            
            st.write(df[["Sentimen", "Pengguna", "Tweet", "Tanggal"]])
            st.download_button(
                        label="Download data",
                        data=csv,
                        file_name='sentiment analysis.csv',
                        mime='text/csv',
                    )
