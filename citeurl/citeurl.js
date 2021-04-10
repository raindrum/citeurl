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
  let match = getMatch(query);
  handleDefaults(match);
  processTokens(match);
  updateUrlParts(match);
  return buildUrl(match);
}

// check the query against each schema one-by-one,
// and return the tokens and schema of the first match
const MATCH_ERROR = "Sorry, I couldn't recognize that citation."
function getMatch(query) {
  for (var i in schemas) {
    var schema = schemas[i];
    var match = false;
    for (var r in schema['regexes']) {
      match = query.match(new RegExp(schema['regexes'][r], 'i'));
      if (match) {
        break;
      }
    }
    if (match) {
      console.log(
        '"' + query + '" matched regex for ' + schema['name']
        + ', and these tokens were found:'
      );
      for (var group in match.groups) {
        console.log(group + ': "' + match.groups[group] + '"');
      }
      console.log(' ');
      return {
        tokens: match.groups,
        schema: schema
      };
    }
  }
  console.log(
    '"' + query + '" did not match the regex for any schema. Check the '
    + 'page source to see the schemas and their regexes.'
  );
  throw Error(MATCH_ERROR);
}

// for each default token value specified by the schema,
// apply it to the relevant token if that token was not set
function handleDefaults(match) {
  let {schema, tokens} = match;
  for (var d in schema.defaults) {
    if (!tokens[d]) {
      console.log(
        d + ' was not specified, so it will be set to "'
        + schema.defaults[d] + '" by default'
      );
      tokens[d] = schema.defaults[d];
      console.log(' ');
    }
  }
}

// for each token processing operation in the schema,
// modify the tokens accordingly
function processTokens(match) {
  let {schema, tokens} = match;
  let appliedAnOperation = false;
  if (!('operations' in schema)) {
    return;
  }
  for (var o in schema.operations) {
    var operation = schema.operations[o];
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
      output = operation['output'];
    }
    else {
      output = operation['token'];
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
        tokens[output] = inputValue.replace(
          /\w\S*/g,
          function (txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
          }
        );
      }
    }
    
    // handle regex substitution
    if ('sub' in operation) {
      let regex = new RegExp(operation['sub'][0], 'ig');
      let outputValue = inputValue.replace(regex, operation['sub'][1]);
      tokens[output] = outputValue;
      console.log(
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
        
        console.log(tokens[operation['token']]);
        
        for (var key in operation[lookupTypes[t]]) {
          let regexStr = '^(' + key + ')$';
          if (tokens[operation['token']].match(new RegExp(regexStr, 'i'))) {
            outputValue = operation[lookupTypes[t]][key];
            break;
          }
        }
        if (outputValue !== undefined) {
          tokens[output] = outputValue;
        }
        else if (lookupTypes[t] == 'optionalLookup') {
          console.log(
            'tried to look up token "' + operation['token'] + '" in an index,'
            + 'but failed, so token "' + output + '" will not be modified.'
          );
        }
        else {
          throw Error(
            "Sorry, I can't find that" + operation['token'] + " in the " + schema
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
      console.log(
        'added zeros to the beginning of ' + operation['token']
        + ' until it was ' + String(operation['lpad']) + ' characters long'
      );
    }
  }
  if (appliedAnOperation) {
    console.log(' ');
  }
}

// go through the pieces of the schema's URL template, and replace any
// section in curly braces with the value of the fully-processed token
// of the same name, Leave placeholders unchanged if they reference
// undefined tokens.
function updateUrlParts(match) {
  let {schema, tokens} = match;
  console.log("replacing placeholders in each part of the URL template...");
  for (var part in schema.URL) {
    console.log('before: "' + schema.URL[part] + '"');
    for (var k in tokens) {
      if (typeof tokens[k] === 'undefined') {
        continue;
      }
      let placeholder = new RegExp("\\{" + k + "\\}", 'g');
      schema.URL[part] = schema.URL[part].replace(placeholder, tokens[k]);
    }
    console.log('after:  "' + schema.URL[part] + '"');
  }
  console.log(' ');
}

// after the placeholders in the URL parts have been filled in,
// concatenate the parts to make a full URL. Omit any part that
// still contains a placeholder
function buildUrl(match) {
  let {schema, tokens} = match;
  let url = '';
  let missingPlaceholder = new RegExp("\\{.+\\}");
  console.log('building URL from parts...');
  for (p in schema.URL) {
  let part = schema.URL[p];
    if (!part.match(missingPlaceholder)) {
      url += part;
      console.log('added "' + part + '"');
    }
    else {
      console.log('omitted "'+part+'" because it still has a placeholder');
    }
  }
  console.log('finished building URL: ' + url);
  return url;
}
