async function display_seasonality_chart(url) {
    /**
     * Fetches seasonality data from the provided URL and displays it in a Highcharts chart.
     *
     * @param {string} url - The URL to fetch the seasonality data from.
     * @returns {Promise<void>} - A promise that resolves when the chart has been successfully created and rendered.
     *
     * The function performs the following steps:
     * 1. Fetches JSON data from the specified URL.
     * 2. Uses Highcharts to create a stock chart with the fetched data.
     * 3. Displays the chart in an HTML container with the ID 'container-chart1'.
     */

  const amount = await fetch(url).then(response => response.json());

  // Create the chart
  Highcharts.stockChart('container-chart1', {
    rangeSelector: {
        selected: 1
    },

    title: {
        text: 'Seasonality'
    },

    series: [{
        name: 'Seasonality',
        data: amount,
        tooltip: {
            valueDecimals: 3
        }
    }]
  });
}



// JUST FOR SEASONALITY -> IGNORE IT
async function display_single_years(url) {
    const data_single_year = await fetch(url+"/history").then(response => response.json());
    
    dict = JSON.parse(data_single_year)
    let chart_series = []

    for (obj in dict) {
        array_list = []
        sub_dict = dict[obj]

        keys = Object.keys(sub_dict)
        for (key in keys) {
            array_list.push(sub_dict[key])
        }

        chart_series.push({
    	    name: obj,
    	    data: array_list
        });
    }

    console.log('Chart series:')
    console.log(chart_series)
  

  


    /**
     * Create the chart when all data is loaded
     * @return {undefined}
     */
    function createChart(series) {

        Highcharts.stockChart('container-chart2', {

            rangeSelector: {
                selected: 4
            },

            yAxis: {
                labels: {
                    format: '{#if (gt value 0)}+{/if}{value}%'
                },
                plotLines: [{
                    value: 0,
                    width: 2,
                    color: 'silver'
                }]
            },

            plotOptions: {
                series: {
                    compare: 'percent',
                    showInNavigator: true
                }
            },

            tooltip: {
                pointFormat: '<span style="color:{series.color}">' +
                    '{series.name}</span>: <b>{point.y}</b> ' +
                    '({point.change}%)<br/>',
                valueDecimals: 2,
                split: true
            },

            series
        });

    }

    createChart(chart_series);



    (async () => {

        const names = ['MSFT', 'AAPL', 'GOOG'];
    
        /**
         * Create the chart when all data is loaded
         * @return {undefined}
         */
        function createChart(series) {
    
            Highcharts.stockChart('container-chart1', {
    
                rangeSelector: {
                    selected: 4
                },
    
                yAxis: {
                    labels: {
                        format: '{#if (gt value 0)}+{/if}{value}%'
                    },
                    plotLines: [{
                        value: 0,
                        width: 2,
                        color: 'silver'
                    }]
                },
    
                plotOptions: {
                    series: {
                        compare: 'percent',
                        showInNavigator: true
                    }
                },
    
                tooltip: {
                    pointFormat: '<span style="color:{series.color}">' +
                        '{series.name}</span>: <b>{point.y}</b> ' +
                        '({point.change}%)<br/>',
                    valueDecimals: 2,
                    split: true
                },
    
                series
            });
    
        }
    
        const promises = names.map(name => new Promise(resolve => {
            (async () => {
                const data = await fetch(
                    'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/' +
                    'samples/data/' + name.toLowerCase() + '-c.json'
                )
                    .then(response => response.json());
                resolve({ name, data });
            })();
        }));
    
        const series = await Promise.all(promises);
        console.log('Series:')
        console.log(series)

        createChart(series);
    
    })();
};





let inputForm = document.getElementById('inputForm')


// The following code is executed when "Submit" button is clicked by the user.
inputForm.addEventListener("submit", (e) => {
  e.preventDefault();

  let start_year = document.getElementById("startYear").value
  let start_month = document.getElementById("startMonth").value
  let start_date = start_year + '-' + start_month + '-' + '01'

  let end_year = document.getElementById("endYear").value
  let end_month = document.getElementById("endMonth").value
  let end_date = end_year + '-' + end_month + '-' + '01'

  let isin = document.getElementById("ISIN").value
      
  let input = {
    "isin": isin,
    "start_year": start_year,
    "start_month": start_month,
    "end_year": end_year,
    "end_month": end_month,
  }

  console.log(input)

  url = 'http://127.0.0.1:8000/' + 'search-etf/' + isin + '/' + start_year + '/' + start_month + '/' + end_year + '/' + end_month
  console.log(url)
  //window.location.href = url

  display_seasonality_chart(url)
  //display_single_years(url)
})