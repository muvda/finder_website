import json
import urllib.request

from flask import Flask, render_template, request, redirect, url_for

from web_scrape import scrape_rating, scrape_outline_for_app

app = Flask(__name__)


@app.route('/')
def home():
    with urllib.request.urlopen("http://www.sfu.ca/bin/wcm/course-outlines/?year=2021&term=fall&search=CMPT") as url:
        courses = json.loads(url.read().decode())
    return render_template('home.html', courses=courses)


@app.route('/your-course', methods=['GET', 'POST'])
def your_course():
    if request.method == 'POST':
        url_suffix = request.form['course']
        outline = scrape_outline_for_app(url_suffix)
        if 'instructors' in outline:
            ratings = []
            for instructor in outline['instructors']:
                rating = scrape_rating(instructor)
                ratings.append(rating)
            return render_template('your_course.html', outline=outline, ratings=ratings)
        return render_template('your_course.html', outline=outline)
    else:
        return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    app.run()
