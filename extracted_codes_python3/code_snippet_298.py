import random
import requests
from bs4 import BeautifulSoup

user_input = input("Press 'T' for Top Rated Movies. Press 'I' for Indian Movies. Press 'L' for Low Rated Movies. Press any other \
key to exit.\n") # user input for Top Rated, Indian, Low Rated Movies.

# Chooses the url based on user input.
if user_input == "T" or user_input == "t":
    url = "https://www.imdb.com/chart/top"
elif user_input == "I" or user_input == "i":
    url = "https://www.imdb.com/india/top-rated-indian-movies"   
elif user_input == "L" or user_input == "l":
    url ="https://www.imdb.com/chart/bottom"
else:
    quit()

def movie_picker():
    response = requests.get(url)
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    tag_movie = soup.select("td.titleColumn")
    innertag_movie = soup.select("td.titleColumn a")
    ratings_tag = soup.select("td.posterColumn span[name = ir]")

    def all_years(year_movies):
        movie_split = year_movies.text.split()
        year = movie_split[-1]
        return year
    
    years = [all_years(year) for year in tag_movie] # appends release year to the list.
    actors_list = [tag["title"] for tag in innertag_movie] # appends names of director and actors to the list.
    movie_titles = [tag.text for tag in innertag_movie] # appends movie titles to the list.
    ratings = [float(tag["data-value"]) for tag in ratings_tag] # gets the rating and converts into float value.

    num_movies = len(movie_titles)
    
    directors_list = []
    actors = []

    for people in actors_list:
        person = people.split(",") # splits the list of lists.
        director = person.pop(0) # collects the name of the director.
        directors_list.append(director[0:len(director)-7]) # removes (dir.) at the end of directors list and appends it to directors_list.
        actors.append(person)   # appends name of the actors to the list.
       
    while True:
        ind = random.randrange(0,num_movies)
    
        print(f"Python Sugession: '{movie_titles[ind]}'  directed by {directors_list[ind]}, \
main roles played by {actors[ind][0]} and {actors[ind][1]}. It was released in the year {years[ind][1:5]}.It has an IMDB \
rating of {ratings[ind]:.1f}.\n")

        user_input = input("Already watched? Do you want another movie? Press 'y' to get another suggesion.\n") # asks user for another suggestion.  

        if user_input != "y":
            print("Enjoy the Movie!! Have a great day.") 
            break    

if __name__ == "__main__":
    movie_picker()