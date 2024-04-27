// importing the fs module for writing json files
// !!!! HERE WE NEED NODEJS (how tf does it work?)
const fs = require("fs");


let inputForm = document.getElementById('inputForm')
let filename = "input.json"

inputForm.addEventListener("submit", (e) => {
  e.preventDefault();

  let amount = document.getElementById("amountControl")
  let ticker = document.getElementById("tickerControl")
  let strategy = document.getElementById("strategyControl")

  if (amount.value == "" || ticker.value == "") {
    alert("Ensure to add a value for both amount and ticker")
  } else {
    
    let input = {
        "amount": parseInt(amount.value),
        "ticker": ticker.value,
        "strategy": strategy.value,
    }

    let inputJSON = JSON.stringify(input)
    console.log(
      `Amount: ${amount.value}, ticker: ${ticker.value}`
    )

    fs.writeFile(filename, inputJSON, (error) => {
        // throwing the error
        // in case of a writing problem
        if (error) {
          // logging the error
          console.error(error);
      
          throw error;
        }
      
        console.log(filename," written correctly");
      });
  }
})

