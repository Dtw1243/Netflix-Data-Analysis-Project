import pandas as pd
import os
import matplotlib.pyplot as plt

os.getcwd()

df = pd.read_csv(
    r'C:\Users\dtw12\OneDrive\Documents\Projects\Data Analytics Projects\Netflix Data Analysis\netflix_titles.csv',
    encoding='latin1'
)


df.shape
df.info()
df.head()
print(df.head())
print(df.info())


df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')

#seperating the by type of media
df['type'].value_counts()

# extracting the month and year from date added
years = df['year_added'] = df['date_added'].dt.year
months = df['month_added'] = df['date_added'].dt.month

# visualizing the genre distribution
# checking which genres and the amount of each genre
genres = df['listed_in'].str.get_dummies(sep=', ')

genre_counts = genres.sum().sort_values(ascending=False)
top_genres = genre_counts.head(15)
plt.figure(figsize=(10,8))
plt.pie(top_genres, labels=top_genres.index, autopct='%1.1f%%', startangle=140)
plt.title('Top 15 Genres on Netflix')
plt.show()


# tv show and movies distribution (seasons and runtime)

tv_shows = df[df['type'] == 'TV Show']
tv_shows['seasons'] = tv_shows['duration'].str.extract('(\\d+)').astype(float)
season_counts = tv_shows['seasons'].value_counts().sort_index()
season_counts.plot(kind='bar', title='Distribution of TV Show Seasons', xlabel='Number of Seasons', ylabel='Count')
plt.show() 

movies =df[df['type'] == 'Movie']
movies['runtime_minutes'] = movies['duration'].str.extract('(\\d+)').astype(float)
plt.hist(movies['runtime_minutes'], bins=30, edgecolor='black')
plt.title('Distribution of Movie Runtimes')
plt.xlabel('Runtime (minutes)')
plt.ylabel('Count')
plt.show()

# checking the distribution of viewer ratings
rating_counts = df['rating'].value_counts()
df.groupby('type')['rating'].value_counts(normalize=True).unstack()

# checking the country of production
country_counts = df['country'].value_counts().head(10)

plt.bar(country_counts.index, country_counts.values)
plt.xticks(rotation=45)
plt.title('Top 10 Countries Producing Content on Netflix')
plt.xlabel('Country')
plt.ylabel('Count')
plt.show()

# analyzing content added over the years 
yearly_counts = df['year_added'].value_counts().sort_index()
yearly_counts.plot(kind='line', title='Content Added Over the Years')
plt.xlabel('Year')
plt.ylabel('Count')
plt.show()
