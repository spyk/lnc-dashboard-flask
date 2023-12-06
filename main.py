
from flask import Flask, render_template, request
from services.model_loader import ModelLoader
from services.search_service import SearchService
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Create an instance of ModelLoader
model_loader = ModelLoader()

# Pass the config and ModelLoader instance to the service class
service = SearchService(app.config, model_loader)

@app.route('/', methods=['GET', 'POST'])
def search():
    search_type = ""
    date_filter = ''
    query = ""
    tokens = []
    bm25_results = []
    vector_results = []
    hybrid_results = []

    if request.method == 'POST':
        query = request.form.get('query')
        search_type = request.form.get('search_type')
        date_filter = request.form.get('date_filter')

        bm25_results = service.bm25_search(query, date_filter)
        tokens, vector_results = service.vector_search(query, date_filter)
        hybrid_results = service.hybrid_search(query, date_filter)

    return render_template(
        'search.html',
        query=query,
        search_type=search_type,
        date_filter=date_filter,
        bm25_results=bm25_results,
        tokens=tokens,
        vector_results=vector_results,
        hybrid_results=hybrid_results
    )

if __name__ == '__main__':
    app.run(debug=True)