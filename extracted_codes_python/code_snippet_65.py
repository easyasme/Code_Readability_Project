import requests
import json
import pymysql
from datetime import datetime

MOVIE = input("Enter the name of the film: ")

def fetch_movie_data(imdb_id, api_key="1f3fc3ff"):
    response = requests.get(f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}")
    
    if response.status_code != 200:
        print("Failed to fetch data from OMDB API.")
        return None
    
    movie_data = response.json()

    if movie_data.get('Response') == 'False':
        print("Movie not found!")
        return None

    title = movie_data.get('Title', 'Unknown')
    released = movie_data.get('Released', 'Unknown')
    genre = movie_data.get('Genre', 'Unknown')
    director = movie_data.get('Director', 'Unknown')

    # Convert date to 'YYYY-MM-DD' format
    if released != 'Unknown':
        try:
            released = datetime.strptime(released, '%d %b %Y').strftime('%Y-%m-%d')
        except ValueError:
            released = None

    return title, released, genre, director

def store_movie_data(connection, movie_info):
    if not movie_info:
        print("No movie data to store.")
        return

    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO Movie_info (title, released, genre, director)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, movie_info)
            connection.commit()
            print("Movie data inserted successfully.")
    except pymysql.MySQLError as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()

# Database connection
connection = pymysql.connect(
    host='localhost',       # Replace with your MySQL server address
    user='mysql',           # Replace with your MySQL username
    password='123456',      # Replace with your MySQL password
    database='mydata',      # Replace with your MySQL database name
    port=3306,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# Fetch movie data
movie_info = fetch_movie_data("tt3896198")

# Store movie data in the database
store_movie_data(connection, movie_info)
