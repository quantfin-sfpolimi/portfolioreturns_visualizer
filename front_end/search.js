// Funzione per eseguire la ricerca fuzzy e visualizzare i risultati
function performSearch(query, data) {
    const fuse = new Fuse(data, {
        keys : ['ISIN', 'FUNDNAME'],
        includeScore: true,
        threshold: 0.3
    });

    const result = fuse.search(query);

    console.log(result)

    const searchResults = document.getElementById('search-results');
    searchResults.innerHTML = '';

    result.forEach(item => {
        const div = document.createElement('div');
        div.textContent = `ISIN: ${item.item.ISIN}, FUNDNAME: ${item.item.FUNDNAME}, Score: ${item.score.toFixed(2)}`;
        searchResults.appendChild(div);
    });
}

// Funzione per gestire l'evento di input sulla barra di ricerca
function handleSearchInput() {
    const query = document.getElementById('search-input').value;
    fetch('big_file.json')
        .then(response => response.json())
        .then(data => performSearch(query, data))
        .catch(error => console.error('Errore durante il recupero dei dati:', error));
}

// Aggiungi un listener per l'evento di input sulla barra di ricerca
document.getElementById('search-input').addEventListener('input', handleSearchInput);
