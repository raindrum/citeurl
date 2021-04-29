// on page load, check whether there's a URL parameter.
// If there is, insert it into the search bar, and run the
// search. Otherwise, unhide the page for normal display.
if (typeof document !== 'undefined') {
  document.addEventListener("DOMContentLoaded", () => {
    if (!location.search) {
      return document.body.removeAttribute('hidden');
    }
    let query = decodeURIComponent(location.search);
    query = query.trim().replace(/^\?(?:q=)?|\.$|,$|;$/g, '');
    document.getElementById("q").value = query.replace(/\+/g, ' ');
    
    handleQuery(query);
  });
}

if (
    typeof window !== 'undefined'
    && typeof window.addEventListener !== 'undefined'
) {
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
}

function log(text) {
  if (typeof console !== 'undefined') {
    console.log(text)
  }
}

class Citation {
  constructor(template, text) {
    // first, try matching the template
    let regexMatch = false;
    for (var r in template['regexes']) {
      regexMatch = text.match(new RegExp(template['regexes'][r], 'i'));
      if (regexMatch) {
        break;
      }
    }
    if (regexMatch) {
      log(
        '"' + text + '" matched regex for ' + template['name']
        + ', and these tokens were found:'
      );
      for (var group in regexMatch.groups) {
        if (typeof group !== 'undefined') {
          log(group + ': "' + regexMatch.groups[group] + '"');
        }
      }
      log(' ');
    }
    else {
      throw Error("The given query does not match the given template.");
    }
    
    this.tokens = regexMatch.groups;
    this.text = text;
    this.template = template['name'];
    
    // this variable will become this.processedTokens
    var tokens = {}
    Object.assign(tokens, this.tokens);
    
    // set default values for missing tokens
    for (var d in template.defaults) {
      if (!tokens[d]) {
        log(
          d + ' was not specified, so it will be set to "'
          + template.defaults[d] + '" by default'
        );
        tokens[d] = template.defaults[d];
        log(' ');
      }
    }
    
    // apply predefined operations to the found tokens
    let appliedAnOperation = false;
    if (!('operations' in template)) {
      return;
    }
    function titleCase (txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    }
    for (var o in template.operations) {
      var operation = template.operations[o];
      var inputValue = tokens[operation['token']];
      
      // skip tokens that were not set
      if (inputValue === undefined) {
        continue;
      }
      else {
        appliedAnOperation = true;
      }
      
      // determine output token
      if ('output' in operation) {
        var output = operation['output'];
      }
      else {
        var output = operation['token'];
      }
      
      // handle case modification
      if ('case' in operation) {
        if (operation['case'] == 'upper') {
          tokens[output] = inputValue.toUpperCase();
        }
        else if (operation['case'] == 'lower') {
          tokens[output] = inputValue.toLowerCase();
        }
        else if (operation['case'] == 'title') {
          tokens[output] = inputValue.replace(/\w\S*/g, titleCase);
        }
      }
      
      // handle regex substitution
      if ('sub' in operation) {
        let regex = new RegExp(operation['sub'][0], 'ig');
        let outputValue = inputValue.replace(regex, operation['sub'][1]);
        tokens[output] = outputValue;
        log(
          'replaced all instances of regex "' + operation['sub'][0] + '" in '
          + 'token "' + operation['token'] + '" with "' + operation['sub'][1]
          + '" to set token "${output}" to "${outputValue}".'
        );
      }
      
      // handle regex lookups
      let lookupTypes = ['lookup', 'optionalLookup'];
      for (var t in lookupTypes) {
        if (lookupTypes[t] in operation) {
          let outputValue;
          
          for (var key in operation[lookupTypes[t]]) {
            let regexStr = '^(' + key + ')$';
            if (tokens[operation['token']].match(new RegExp(regexStr, 'i'))) {
              outputValue = operation[lookupTypes[t]][key];
              log(
                'Looked up ' + operation['token'] + ' "'
                + tokens[operation['token']] + '" in a table, and used that '
                + 'to set ' + output + ' to "' + outputValue + '"' 
              );
              break;
            }
          }
          if (outputValue !== undefined) {
            tokens[output] = outputValue;
          }
          else if (lookupTypes[t] == 'optionalLookup') {
            log(
              'tried to look up token "' + operation['token'] + '" in an index,'
              + 'but failed, so token "' + output + '" will not be modified.'
            );
          }
          else {
            throw Error(
              "Sorry, I can't find that" + operation['token'] + " in the " + template
            );
          }
        }
      }
      
      // Bidirectional conversion between digits and roman numerals. This method
      // is lazy and only goes up to 100, but if you need it to go higher, you
      // can just add more numeral-digit pairs to the list.
      if ('numberFormat' in operation) {
        let numerals = [
          ['I', '1'], ['II', '2'], ['III', '3'], ['IV', '4'], ['V', '5'],
          ['VI', '6'], ['VII', '7'], ['VIII', '8'], ['IX', '9'], ['X', '10'],
          ['XI', '11'], ['XII', '12'], ['XIII', '13'], ['XIV', '14'],
          ['XV', '15'], ['XVI', '16'], ['XVII', '17'], ['XVIII', '18'],
          ['XIX', '19'], ['XX', '20'], ['XXI', '21'], ['XXII', '22'],
          ['XXIII', '23'], ['XXIV', '24'], ['XXV', '25'], ['XXVI', '26'], 
          ['XXVII', '27'], ['XXVIII', '28'], ['XXIX', '29'], ['XXX', '30'],
          ['XXXI', '31'], ['XXXII', '32'], ['XXXIII', '33'], ['XXXIV', '34'],
          ['XXXV', '35'], ['XXXVI', '36'], ['XXXVII', '37'], ['XXXVIII', '38'],
          ['XXXIX', '39'], ['XL', '40'], ['XLI', '41'], ['XLII', '42'],
          ['XLIII', '43'], ['XLIV', '44'], ['XLV', '45'], ['XLVI', '46'],
          ['XLVII', '47'], ['XLVIII', '48'], ['XLIX', '49'], ['L', '50'],
          ['LI', '51'], ['LII', '52'], ['LIII', '53'], ['LIV', '54'],
          ['LV', '55'], ['LVI', '56'], ['LVII', '57'], ['LVIII', '58'],
          ['LIX', '59'], ['LX', '60'], ['LXI', '61'], ['LXII', '62'],
          ['LXIII', '63'], ['LXIV', '64'], ['LXV', '65'], ['LXVI', '66'],
          ['LXVII', '67'], ['LXVIII', '68'], ['LXIX', '69'], ['LXX', '70'],
          ['LXXI', '71'], ['LXXII', '72'], ['LXXIII', '73'], ['LXXIV', '74'],
          ['LXXV', '75'], ['LXXVI', '76'], ['LXXVII', '77'], ['LXXVIII', '78'],
          ['LXXIX', '79'], ['LXXX', '80'], ['LXXXI', '81'], ['LXXXII', '82'],
          ['LXXXIII', '83'], ['LXXXIV', '84'], ['LXXXV', '85'],
          ['LXXXVI', '86'], ['LXXXVII', '87'], ['LXXXVIII', '88'],
          ['LXXXIX', '89'], ['XC', '90'], ['XCI', '91'], ['XCII', '92'],
          ['XCIII', '93'], ['XCIV', '94'], ['XCV', '95'], ['XCVI', '96'],
          ['XCVII', '97'], ['XCVIII', '98'], ['XCIX', '99'], ['C', '100']
        ];
        // determine which format is being used to look up the other
        let key, value;
        if (operation['numberFormat'] == 'roman') {
          key = 1;
          value = 0;
        }
        else if (operation['numberFormat'] == 'digit') {
          key = 0;
          value = 1;
        }
        // perform the appropriate lookup, outputting the input value
        // unchanged if the lookup fails
        tokens[output] = inputValue;
        for (var pair in numerals) {
          if (numerals[pair][key].match(inputValue.toUpperCase())) {
            tokens[output] = numerals[pair][value];
            log(
              'translated ' + operation['token'] + ' to '
              + operation['numberFormat'] + " format if it wasn't already, and"
              + ' saved the result (' + tokens[output] + ') to ' + output
            );
            break;
          }
        }
      }
      
      // left pad with zeros
      if ('lpad' in operation) {
        let outputValue = inputValue;
        while (outputValue.length < operation['lpad']) {
          outputValue = '0' + outputValue;
        }
        tokens[output] = outputValue
        log(
          'added zeros to the beginning of ' + operation['token']
          + ' until it was ' + String(operation['lpad']) + ' characters long,'
          + ' and saved the result to ' + tokens[output]
        );
      }
    }
    if (appliedAnOperation) {
      log(' ');
    }
    this.processedTokens = tokens;
    
    // finally, fill in placeholders in the URL template to generate the
    // URL, skipping any sections of the template that contain a missing
    // placeholder.
    let URL = [];
    let missingPlaceholder = new RegExp("\\{.+\\}");
    log("filling in placeholders in each part of the URL template...");
    for (var part in template.URL) {
      let URLPart = template.URL[part]
      for (var k in this.processedTokens) {
        if (typeof this.processedTokens[k] === 'undefined') {
          continue;
        }
        let placeholder = new RegExp("\\{" + k + "\\}", 'g');
        URLPart = URLPart.replace(placeholder, this.processedTokens[k]);
      }
      if (!URLPart.match(missingPlaceholder)) {
        URL.push(URLPart);
        log('"' + template.URL[part] + '"   -->   "' + URLPart + '"')
      }
      else {
        log(
          'omitting "' + template.URL[part]
          + '" since it references a missing placeholder'
        )
      }
    }
    this.URL = URL.join('');
    log('Finished building URL: "' + this.URL + '"');
    log(' ');
  }
}

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
    log(
      '"' + query + '" did not match the regex for any template. Check the '
      + 'page source to see the templates and their regexes.'
    );
    throw Error(MATCH_ERROR);
  }
  return citations;
}
