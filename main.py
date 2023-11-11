
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def search():
    search_type = ""
    filters = "BM25"
    query = ""

    if request.method == 'POST':
        query = request.form.get('query')
        search_type = request.form.get('search_type')
        filters = request.form.get('filters')

        # Add your search logic here

    return render_template('search.html', query=query, search_type=search_type, filters=filters)

if __name__ == '__main__':
    app.run(debug=True)