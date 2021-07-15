/*PAGEBEHAVIOR
// on page load, check whether there's a URL parameter.
// If there is, insert it into the search bar, and run the
// search. Otherwise, unhide the page for normal display.
document.addEventListener("DOMContentLoaded", () => {
if (!location.search) {
  return document.body.removeAttribute('hidden');
}
let query = decodeURIComponent(location.search);
query = query.trim().replace(/^\?(?:q=)?|\.$|,$|;$/g, '');
document.getElementById("q").value = query.replace(/\+/g, ' ');

handleQuery(query);
});

window.addEventListener( "pageshow", function ( event ) {
var historyTraversal = event.persisted || (
  typeof window.performance != "undefined" &&
  window.performance.navigation.type === 2
);
if ( historyTraversal ) {
  // Handle page restore.
  window.location.reload();
}
});

*/
/*LOGS
function log(text) {
  console.log(text)
}
*/

class Citation {
  constructor(template, text) {
    // first, try matching the template
    let regexMatch = false;
    for (var r in template.regexes) {
      regexMatch = text.match(new RegExp(template.regexes[r], 'i'));
      if (regexMatch) {
        break;
      }
    }
    if (!regexMatch) {
      throw Error("The given query does not match the given template.");
    }
    /*LOGS
    else {
      log(
        '"' + text + '" matched regex for ' + template['name']
        + ', and these tokens were found:'
      );
      for (var group in regexMatch.groups) {
        if (typeof group !== 'undefined') {
          log(group + ': "' + regexMatch.groups[group] + '"');
        }
      }
    }
    log(' ');
    */
    
    this.tokens = regexMatch.groups;
    this.text = text;
    this.template = template.name;
    
    // this variable will become this.processedTokens
    var tokens = {};
    Object.assign(tokens, this.tokens);
    
    // set default values for missing tokens
    for (var d in template.defaults) {
      if (!tokens[d]) {
        /*LOGS
        log(
          d + ' was not specified, so it will be set to "'
          + template.defaults[d] + '" by default\n '
        );
        */
        tokens[d] = template.defaults[d];
      }
    }
    
    // apply predefined operations to the found tokens
    let appliedAnOperation = false;
    function titleCase (txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    }
    for (var o in template.operations) {
      var operation = template.operations[o];
      var inputValue = tokens[operation.token];
      
      // skip tokens that were not set
      if (inputValue === undefined) {
        continue;
      }
      else {
        appliedAnOperation = true;
      }
      
      // determine output token
      var output;
      if ('output' in operation) {
        output = operation.output;
      }
      else {
        output = operation.token;
      }
      
      // handle case modification
      if ('case' in operation) {
        if (operation.case == 'upper') {
          tokens[output] = inputValue.toUpperCase();
        }
        else if (operation.case == 'lower') {
          tokens[output] = inputValue.toLowerCase();
        }
        else if (operation.case == 'title') {
          tokens[output] = inputValue.replace(/\w\S*/g, titleCase);
        }
      }
      
      // handle regex substitution
      if ('sub' in operation) {
        let regex = new RegExp(operation.sub[0], 'ig');
        let outputValue = inputValue.replace(regex, operation.sub[1]);
        tokens[output] = outputValue;
        /*LOGS
        log(
          'replaced all instances of regex "' + operation.sub[0] + '" in '
          + 'token "' + operation.token + '" with "' + operation.sub[1]
          + '" to set token "${output}" to "${outputValue}".'
        );
        */
      }
      
      // handle regex lookups
      let lookupTypes = ['lookup', 'optionalLookup'];
      for (var t in lookupTypes) {
        if (lookupTypes[t] in operation) {
          let outputValue;
          
          for (var key in operation[lookupTypes[t]]) {
            let regexStr = '^(' + key + ')$';
            if (tokens[operation.token].match(new RegExp(regexStr, 'i'))) {
              outputValue = operation[lookupTypes[t]][key];
              /*LOGS
              log(
                'Looked up ' + operation.token + ' "'
                + tokens[operation.token] + '" in a table, and used that '
                + 'to set ' + output + ' to "' + outputValue + '"' 
              );
              */
              break;
            }
          }
          if (outputValue !== undefined) {
            tokens[output] = outputValue;
          }
          /*LOGS
          else if (lookupTypes[t] == 'optionalLookup') {
            log(
              'tried to look up token "' + operation.token + '" in an index,'
              + 'but failed, so token "' + output + '" will not be modified.'
            );
          }
          */
          else {
            throw Error(
              "Sorry, I can't find that" + operation.token + " in the " + template
            );
          }
        }
      }
      
      // Bidirectional conversion between digits and roman numerals. This method
      // is lazy and only goes up to 100, but if you need it to go higher, you
      // can just add more numeral-digit pairs to the list.
      if ('number_style' in operation) {
        let numerals = [
          ['i', '1', 'one', 'first'], ['ii', '2', 'two', 'second'],
          ['iii', '3', 'three', 'third'], ['iv', '4', 'four', 'fourth'],
          ['v', '5', 'five', 'fifth'], ['vi', '6', 'six', 'sixth'],
          ['vii', '7', 'seven', 'seventh'], ['viii', '8', 'eight', 'eighth'],
          ['ix', '9', 'nine', 'ninth'], ['x', '10', 'ten', 'tenth'],
          ['xi', '11', 'eleven', 'eleventh'],
          ['xii', '12', 'twelve', 'twelfth'],
          ['xiii', '13', 'thirteen', 'thirteenth'],
          ['xiv', '14', 'fourteen', 'fourteenth'],
          ['xv', '15', 'fifteen', 'fifteenth'],
          ['xvi', '16', 'sixteen', 'sixteenth'],
          ['xvii', '17', 'seventeen', 'seventeenth'],
          ['xviii', '18', 'eighteen', 'eighteenth'],
          ['xix', '19', 'nineteen', 'nineteenth'],
          ['xx', '20', 'twenty', 'twentieth'], ['xxi', '21'], ['xxii', '22'],
          ['xxiii', '23'], ['xxiv', '24'], ['xxv', '25'], ['xxvi', '26'],
          ['xxvii', '27'], ['xxviii', '28'], ['xxix', '29'],
          ['xxx', '30', 'thirty', 'thirtieth'], ['xxxi', '31'],
          ['xxxii', '32'], ['xxxiii', '33'], ['xxxiv', '34'], ['xxxv', '35'],
          ['xxxvi', '36'], ['xxxvii', '37'], ['xxxviii', '38'],
          ['xxxix', '39'], ['xl', '40', 'forty', 'fortieth'], ['xli', '41'],
          ['xlii', '42'], ['xliii', '43'],['xliv', '44'], ['xlv', '45'],
          ['xlvi', '46'], ['xlvii', '47'], ['xlviii', '48'], ['xlix', '49'],
          ['l', '50', 'fifty', 'fiftieth'], ['li', '51'], ['lii', '52'],
          ['liii', '53'], ['liv', '54'], ['lv', '55'], ['lvi', '56'],
          ['lvii', '57'], ['lviii', '58'], ['lix', '59'],
          ['lx', '60', 'sixty', 'sixtieth'], ['lxi', '61'], ['lxii', '62'],
          ['lxiii', '63'], ['lxiv', '64'], ['lxv', '65'], ['lxvi', '66'],
          ['lxvii', '67'], ['lxviii', '68'], ['lxix', '69'],
          ['lxx', '70', 'seventy', 'seventieth'], ['lxxi', '71'],
          ['lxxii', '72'], ['lxxiii', '73'], ['lxxiv', '74'], ['lxxv', '75'],
          ['lxxvi', '76'], ['lxxvii', '77'], ['lxxviii', '78'],
          ['lxxix', '79'], ['lxxx', '80', 'eighty', 'eightieth'],
          ['lxxxi', '81'], ['lxxxii', '82'], ['lxxxiii', '83'],
          ['lxxxiv', '84'], ['lxxxv', '85'], ['lxxxvi', '86'],
          ['lxxxvii', '87'], ['lxxxviii', '88'], ['lxxxix', '89'],
          ['xc', '90', 'ninety', 'ninetieth'], ['xci', '91'], ['xcii', '92'],
          ['xciii', '93'], ['xciv', '94'], ['xcv', '95'], ['xcvi', '96'],
          ['xcvii', '97'], ['xcviii', '98'], ['xcix', '99'],
          ['c', '100', 'one-hundred', 'one-hundredth']
        ];
        // write the rest of the cardinal and ordinal numbers
        let tensPlace;
        let onesPlace;
        for (row in numerals) {
          if (numerals[row].length > 2) {
            tensPlace = numerals[row][2];
          }
          else {
            onesPlace = (row + 1) % 10;
            numerals[row] = [
              numerals[row][0],
              numerals[row][1],
              tensPlace + '-' + numerals[onesPlace][2],
              tensPlace + '-' + numerals[onesPlace][3],
            ];
          }
        }
        
        // determine which format is being used to look up the other
        let target;
        if (operation.number_style == 'roman') {
          target = 0;
        }
        else if (operation.number_style == 'digit') {
          target = 1;
        }
        else if (operation.number_style == 'cardinal') {
          target = 2;
        }
        else if (operation.number_style == 'ordinal') {
          target = 3;
        }
        // perform the appropriate lookup, outputting the input value
        // unchanged if the lookup fails
        tokens[output] = inputValue;
        let key = inputValue.toLowerCase();
        let matched = false;
        for (var row in numerals) {
          for (var col in numerals[row]) {
            if (numerals[row][col] == key) {
              tokens[output] = numerals[row][target];
              /*LOGS
              log(
                'translated ' + operation.token + ' to '
                + operation.number_style + " format if it wasn't already, and"
                + ' saved the result (' + tokens[output] + ') to ' + output
              );
              */
              matched = true;
              break;
            }
          }
          if (matched) {
            break;
          }
        }
      }
      
      // left pad with zeros
      if ('lpad' in operation) {
        let outputValue = inputValue;
        while (outputValue.length < operation.lpad) {
          outputValue = '0' + outputValue;
        }
        tokens[output] = outputValue;
        /*LOGS
        log(
          'added zeros to the beginning of ' + operation['token']
          + ' until it was ' + String(operation['lpad']) + ' characters long,'
          + ' and saved the result to ' + tokens[output]
        );
        */
      }
    }
    /*LOGS
    if (appliedAnOperation) {
      log(' ');
    }
    */
    this.processedTokens = tokens;
    
    // finally, fill in placeholders in the URL template to generate the
    // URL, skipping any sections of the template that contain a missing
    // placeholder.
    let URL = [];
    let missingPlaceholder = new RegExp("\\{.+\\}");
    /*LOGS
    log("filling in placeholders in each part of the URL template...");
    */
    for (var part in template.URL) {
      let URLPart = template.URL[part];
      for (var k in this.processedTokens) {
        if (typeof this.processedTokens[k] === 'undefined') {
          continue;
        }
        let placeholder = new RegExp("\\{" + k + "\\}", 'g');
        URLPart = URLPart.replace(placeholder, this.processedTokens[k]);
      }
      if (!URLPart.match(missingPlaceholder)) {
        URL.push(URLPart);
        /*LOGS
        log('"' + template.URL[part] + '"   -->   "' + URLPart + '"')
        */
      }
      /*LOGS
      else {
        log(
          'omitting "' + template.URL[part]
          + '" since it references a missing placeholder'
        )
      }
      */
    }
    this.URL = URL.join('');
    /*LOGS
    log('Finished building URL: "' + this.URL + '"\n ');
    */
  }
}

/*PAGEBEHAVIOR
// run search from form entry
function handleSearch(event) {
  event.preventDefault()
  let query = document.getElementById("q").value;
  handleQuery(query);
}

// run search from URL parameter
function handleQuery(query) {
  try {
    // if no query provided, clear the search bar
    if (!query) {
      document.getElementById("explainer").innerHTML = "";
      return;
    }
    window.location.href = getUrlForQuery(query);
  }
  // on error, unhide the page and display explainer
  catch (error) {
    document.body.removeAttribute('hidden');
    document.getElementById("explainer").innerHTML = error.message;
  }
}
*/

// perform each step to convert query into URL
function getUrlForQuery(query) {
  let citation = getCitations(query, true);
  return citation.URL;
}

// check the query against each template one-by-one,
// and return the tokens and template of the first match
const MATCH_ERROR = "Sorry, I couldn't recognize that citation.";
function getCitations(query, returnFirst) {
  var citations = [];
  for (var i in templates) {
    let citation = false;
    try {
      citation = new Citation(templates[i], query);
      if (returnFirst) { return citation }
      citations.push(citation);
    }
    catch (error) {
      continue;
    }
  }
  if (returnFirst) {
    /*LOGS
    log(
      '"' + query + '" did not match the regex for any template. Check the '
      + 'page source to see the templates and their regexes.'
    );
    */
    throw Error(MATCH_ERROR);
  }
  return citations;
}
