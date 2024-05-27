// Array per memorizzare i ticker selezionati con le rispettive percentuali
let selectedTickers = [];
let weights = [];
let isTerApplied = false;

function toggleFunds() {
    const button = document.getElementById('toggle-funds');
    isTerApplied = !isTerApplied;
    button.textContent = isTerApplied ? 'Yes' : 'No';
    button.classList.toggle('btn-primary', isTerApplied);
    button.classList.toggle('btn-secondary', !isTerApplied);
    console.log("Funds Applied: ", isTerApplied);
}

function toggleInvestmentFields() {
    const investmentType = document.getElementById('investmentType').value;
    const recurringFields = document.getElementById('recurringFields');

    if (investmentType === 'recurring') {
        recurringFields.style.display = 'block';
    } else {
        recurringFields.style.display = 'none';
    }
}

// Function to ensure positive values for amounts
function validatePositiveAmount(event) {
    const value = event.target.value;
    if (value < 0) {
        event.target.value = 0;
    }
}

// Function to ensure frequency is between 1 and 12
function validateFrequency(event) {
    const value = event.target.value;
    if (value < 1) {
        event.target.value = 1;
    } else if (value > 12) {
        event.target.value = 12;
    }
}

// Funzione per eseguire la ricerca fuzzy e visualizzare i risultati
function performSearch(query, data) {
    const fuse = new Fuse(data, {
        keys: ['ISIN', 'FUNDNAME', 'TICKER'],
        includeScore: true,
        threshold: 0.3
    });

    const result = fuse.search(query);

    console.log(result);

    const searchResults = document.getElementById('search-results');
    searchResults.innerHTML = '';

    result.forEach(item => {
        const option = document.createElement('option');
        option.value = item.item.TICKER;
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

// Aggiungi un listener per l'evento di change sul select
document.getElementById('search-results').addEventListener('change', function() {
    const selectedOption = this.options[this.selectedIndex];
    document.getElementById('search-input').value = selectedOption.value; // Scrivi il TICKER nella barra di ricerca
});

// Aggiungi un listener per il pulsante "Add Ticker"
document.getElementById('add-ticker-button').addEventListener('click', function() {
    const ticker = document.getElementById('search-input').value;
    const percentage = parseFloat(document.getElementById('percentage-input').value);

    if (ticker && !isNaN(percentage) && percentage > 0 && percentage <= 100) {
        const totalPercentage = selectedTickers.reduce((sum, item) => sum + item.percentage, 0) + percentage;

        if (totalPercentage <= 100) {
            selectedTickers.push({ ticker, percentage });
            weights.push(percentage);
            updateSelectedTickersList();
            document.getElementById('percentage-input').value = ''; // Pulisci il campo percentuale
        } else {
            alert('La somma delle percentuali non può superare il 100%.');
        }
    } else {
        alert('Inserisci un ticker valido e una percentuale tra 0 e 100.');
    }
});

// Funzione per aggiornare la lista dei ticker selezionati
function updateSelectedTickersList() {
    const selectedTickersList = document.getElementById('selected-tickers-list');
    selectedTickersList.innerHTML = '';

    selectedTickers.forEach(item => {
        const li = document.createElement('li');
        li.textContent = `${item.ticker}: ${item.percentage}%`;
        li.className = 'list-group-item';
        selectedTickersList.appendChild(li);
    });

    // Stampa la lista dei ticker selezionati e i pesi nel log della console
    console.log('Selected Tickers:', selectedTickers);
    console.log('Weights:', weights);
}

// Attach validation to amount inputs
document.getElementById('amount').addEventListener('input', validatePositiveAmount);
document.getElementById('recurringAmount').addEventListener('input', validatePositiveAmount);

// Attach validation to frequency input
document.getElementById('frequency').addEventListener('input', validateFrequency);
