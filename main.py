from flask import Flask, render_template, url_for, request
from data import queries
import math
from dotenv import load_dotenv

load_dotenv()
app = Flask('codecool_series')

@app.route('/')
def index():
    shows = queries.get_shows()
    return render_template('index.html', shows=shows)


@app.route('/design')
def design():
    return render_template('design.html')

@app.route('/show/<int:show_id>')
def movie_desc(show_id):
    show=queries.get_show(show_id)
    actors=queries.get_actors(show_id)
    show_actors = []
    for actor in actors:
        show_actors.append(actor['actors'])
    show_actors = ", ".join(show_actors)
    show['trailer_id'] = \
        show['trailer'][show['trailer'].find('=') + 1:] if show['trailer'] else ''
    return render_template('movie_desc.html', show=show, actors=show_actors)


@app.route('/shows/most-rated/')
@app.route('/shows/most-rated/<int:page>/')
def shows_most_rated(page=1):
    sort = request.args.get('sort', 'rating')
    order = request.args.get('order', ' DESC')

    shows = queries.get_most_rated_shows(page, sort, order)

    page_number = queries.get_page_number()['num']
    from_num = page-2 if page > 3 else 1
    from_num = page-3 if page == page_number-2 else page-4 if page == page_number-1 else from_num
    to_num = page if page == page_number else page + 1 if page == page_number - 1 else page + 3
    to_num = page + 4 if page == 2 else page + 5 if page == 1 else to_num

    print(sort,order)

    return render_template('most_rated.html', title='Most rated shows',
                           shows=shows, num=page_number, current_page=page,
                           from_num=from_num, to_num=to_num, sort=sort, order=order)


def main():
    app.run(debug=False)


if __name__ == '__main__':
    main()
