
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
    filters = "BM25"
    query = ""
    tokens = []
    bm25_results = []
    vector_results = []

    if request.method == 'POST':
        query = request.form.get('query')
        search_type = request.form.get('search_type')
        filters = request.form.get('filters')

        bm25_results = service.bm25_search(query)
        tokens, vector_results = service.vector_search(query)

    return render_template(
        'search.html',
        query=query,
        search_type=search_type,
        filters=filters,
        bm25_results=bm25_results,
        tokens=tokens,
        vector_results=vector_results
    )

if __name__ == '__main__':
    app.run(debug=True)