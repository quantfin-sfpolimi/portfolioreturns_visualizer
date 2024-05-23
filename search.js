// Variabile per salvare l'ISIN selezionato
let selectedISIN = '';
 
// Funzione per eseguire la ricerca fuzzy e visualizzare i risultati
function performSearch(query, data) {
    const fuse = new Fuse(data, {
        keys: ['ISIN', 'FUNDNAME', 'TICKER'],
        includeScore: true,
        threshold: 0.3
    });
 
    const result = fuse.search(query, {limit:4});
 
    const searchResults = document.getElementById('search-results');
    searchResults.innerHTML = '';
 
    result.forEach(item => {
        const option = document.createElement('option');
        option.value = item.item.ISIN;
        option.textContent = `ISIN: ${item.item.ISIN}, FUNDNAME: ${item.item.FUNDNAME}, TICKER: ${item.item.TICKER}`;
        searchResults.appendChild(option);
    });
 
    searchResults.style.display = result.length > 0 ? 'block' : 'none';
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
 
// Aggiungi un listener per l'evento di cambio sul select
document.getElementById('search-results').addEventListener('change', function() {
    const selectedOption = this.options[this.selectedIndex];
    selectedISIN = selectedOption.value; // Salva l'ISIN selezionato
    document.getElementById('selected-result').textContent = `You selected: ${selectedOption.textContent}`;
});
 
// Aggiungi un listener per l'evento di change sul select
document.getElementById('search-results').addEventListener('change', function() {
    const selectedOption = this.options[this.selectedIndex];
    selectedISIN = selectedOption.value; // Salva l'ISIN selezionato
    document.getElementById('selected-result').textContent = `You selected: ${selectedOption.textContent}`;
    console.log(selectedISIN); // Stampa l'ISIN selezionato
    document.getElementById('ISIN').value = selectedISIN
});