import requests
from flask import Flask, render_template, request, redirect, url_for
import fitz  # Importez la bibliothèque PyMuPDF

app = Flask(__name__)

# Chemin du fichier PDF par défaut
pdf_path = '/chemin/vers/votre/fichier.pdf'

# Fonction pour obtenir les détails d'un livre par clé depuis l'API Open Library
def get_book_details_by_key(key):
    url = f'https://openlibrary.org/{key}.json'
    response = requests.get(url)
    
    if response.status_code == 200:
        book_details = response.json()
        
        # Ajoutez le lien de lecture en ligne à partir des données de l'API Open Library
        if 'ocaid' in book_details:
            book_details['read_url'] = f'https://openlibrary.org/{book_details["ocaid"]}'
        else:
            book_details['read_url'] = None
        
        return book_details
    else:
        print(f'La requête vers l\'API Open Library a échoué avec le code {response.status_code}')
        return None

# Cette route affiche le contenu du PDF
@app.route('/lire_pdf/<string:key>')
def lire_pdf(key):
    # Ouvrir le fichier PDF
    pdf_document = fitz.open(pdf_path)

    # Initialiser une liste pour stocker le texte extrait
    texte_pages = []

    # Extraire le texte de chaque page du PDF
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        page_text = page.get_text()
        texte_pages.append(page_text)

    # Fermer le fichier PDF
    pdf_document.close()

    # Obtenir les détails du livre en utilisant la clé
    book_details = get_book_details_by_key(key)

    return render_template('lire_pdf.html', texte_pages=texte_pages, book_details=book_details)

# Gestion de la soumission du formulaire
@app.route('/rechercher', methods=['POST'])
def rechercher():
    name = request.form.get('name')
    if name:
        book_results = []

        # Effectuez une requête à l'API Open Library pour obtenir les résultats
        url = f'https://openlibrary.org/search.json?q={name}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'docs' in data:
                for book_data in data['docs']:
                    book_results.append({
                        'title': book_data['title'] if 'title' in book_data else 'Inconnu',
                        'author_name': ', '.join(book_data['author_name']) if 'author_name' in book_data else 'Inconnu',
                        'key': book_data['key'],
                    })

        if book_results:
            return render_template('resultats.html', book_results=book_results)

    return redirect(url_for('accueil'))

# Vue pour afficher les détails du livre
@app.route('/details/<string:key>')
def details(key):
    book_details = get_book_details_by_key(key)
    if book_details:
        return render_template('details.html', book_details=book_details)
    else:
        return redirect(url_for('accueil'))

# Page d'accueil
@app.route('/')
def accueil():
    return render_template('accueil.html', book_results=None)

if __name__ == '__main__':
    app.run(debug=True)
