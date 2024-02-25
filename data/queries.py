from data import data_manager
from psycopg2 import sql


def get_shows():
    return data_manager.execute_select('SELECT id, title FROM shows;')


def get_show(show_id):
    return data_manager.execute_select("""
            SELECT
                title,
                runtime,
                CONCAT(ROUND(rating, 1)) AS rating,
                STRING_AGG(genres.name, ', ') AS genres,
                trailer,
                overview
            FROM shows
            LEFT JOIN show_genres ON shows.id = show_genres.show_id
            LEFT JOIN genres ON genres.id = show_genres.genre_id
            WHERE shows.id = %(show_id)s
            GROUP BY shows.id
        """, {"show_id":show_id}, fetchall=False)

def get_actors(show_id):
    return data_manager.execute_select("""
    SELECT actors.name AS actors FROM shows
            LEFT JOIN show_characters ON show_characters.show_id = shows.id
            LEFT JOIN actors ON actors.id = show_characters.actor_id
            WHERE shows.id = %(show_id)s
            ORDER BY actor_id
            LIMIT 3
    """, {"show_id": show_id})
def get_most_rated_shows(page_num=1, sort_column='rating', sort_direction='ASC'):
    valid_sort_columns = ['title', 'year', 'runtime', 'rating', 'genres', 'homepage']

    if sort_column.lower() not in valid_sort_columns:
        sort_column = 'rating'

    if sort_direction.upper() not in ['ASC', 'DESC']:
        sort_direction = 'DESC'

    query = """
            SELECT title, 
                   TO_CHAR(year, 'YYYY') AS year, 
                   runtime,
                   ROUND(rating, 2) AS rating, 
                   COALESCE(trailer, 'No URL') AS trailer,
                   STRING_AGG(genres.name, ', ') AS genres, 
                   homepage 
            FROM shows
            LEFT JOIN show_genres ON shows.id = show_genres.show_id
            LEFT JOIN genres ON genres.id = show_genres.genre_id
            GROUP BY shows.id
            ORDER BY 
                CASE %(sort_column)s
                    WHEN 'title' THEN title
                    WHEN 'year' THEN year::text
                    WHEN 'runtime' THEN runtime::text
                    WHEN 'rating' THEN rating::text

                    WHEN 'homepage' THEN homepage
                END """+sort_direction+"""
            OFFSET (%(page_num)s-1)*15 LIMIT 15;
        """
    return data_manager.execute_select(query, {'page_num': page_num, 'sort_column': sort_column})

# def get_most_rated_shows(sort='title', order='asc', page=1):
#     if order == 'asc':
#         danger_direction = 'ASC'
#     else:
#         danger_direction = 'DESC'
#     query = '''
#             SELECT title, TO_CHAR(year,'YYYY') AS year, runtime,
#             COALESCE(homepage, 'no url') AS homepage,
#             COALESCE(trailer, 'no url') AS trailer,
#             ROUND(rating,1) AS rating,
#             STRING_AGG(genres.name, ', ') AS genre
#             FROM shows
#             LEFT JOIN show_genres ON shows.id = show_genres.show_id
#             LEFT JOIN genres ON genres.id = show_genres.genre_id
#             GROUP BY shows.id
#             ORDER BY
#             CASE %(sort)s
#                 when 'title' then title
#                 when 'year' then shows.year
#             END
#             '''+danger_direction+' LIMIT 15 OFFSET ((%(page)s -1) * 15);'
#
#     return data_manager.execute_select(query, {'page': page, 'sort': sort, 'order': order})



def get_page_number():
    return data_manager.execute_select('''
    SELECT COUNT(*) / 15 AS num FROM shows;
    ''', fetchall=False)
