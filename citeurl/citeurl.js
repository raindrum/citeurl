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
  handleMutations(match);
  handleSubstitutions(match);
  updateUrlParts(match);
  return buildUrl(match);
}

// check the query against each schema one-by-one,
// and return the tokens and schema of the first match
const MATCH_ERROR = "Sorry, I couldn't recognize that citation."
function getMatch(query) {
  for (var i = 0; i < schemas.length; i++) {
    var schema = schemas[i];
    var match = query.match(new RegExp(schema['regex'], 'i'));
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

// for each mutation specified by the schema, modify
// the relevant token in place
function handleMutations(match) {
  let {schema, tokens} = match;
  for (var m in schema.mutations) {
    let mutation = schema.mutations[m];
    if (typeof tokens[mutation['token']] === 'undefined') {
      continue;
    }
    let token = tokens[mutation['token']];
    if (!token) {
      continue;
    }
    if ('omit' in mutation) {
      let omission = new RegExp(mutation['omit'], 'g');
      token = token.replace(omission, '');
    }
    if (('splitter' in mutation) & ('joiner' in mutation)) {
      let splitter = new RegExp(mutation['splitter'], 'g');
      let split_token = token.split(splitter).filter(Boolean);
      token = split_token.join(mutation['joiner']);
    }
    if ('case' in mutation) {
      if (mutation['case'] == 'upper') {
        token = token.toUpperCase();
      }
      else if (mutation['case'] == 'lower') {
        token = token.toLowerCase();
      }
    }
    console.log(
      'performed string mutation to turn ' + mutation['token'] + ' "'
      + tokens[mutation['token']] + '" into "' + token + '"'
    );
    tokens[mutation['token']] = token;
  }
  console.log(' ');
}

// for each substitution specified by the schema, look up the token in an
// index, and set it (or the outputToken) to the corresponding value.
// Optionally use regex matching for the index lookup. Throw an error If
// a token is out of index, unless allowUnmatched is set, in which case
// leave it unmodified.
const SUBSTITUTION_ERROR = "Sorry, I can't find that {token} in the {schema}."
function handleSubstitutions(match) {
  let {schema, tokens} = match;
  for (var s in schema.substitutions) {
  let sub = schema.substitutions[s];
  if (tokens[sub['token']] === undefined) {
    continue;
  }
  let outputToken;
  if ('outputToken' in sub) {
    outputToken = sub['outputToken'];
  }
  else {
    outputToken = sub['token'];
  }
  let newToken;
  if (sub['useRegex']) {
    for (var token in sub['index']) {
      var regexStr = '^(' + token + ')$';
      if (tokens[sub['token']].match(new RegExp(regexStr, 'i'))) {
        newToken = sub['index'][token];
        break;
      }
    }
  }
  else {
    newToken = sub['index'][tokens[sub['token']]];
    if (newToken === undefined) {
      newToken = sub['index'][tokens[sub['token']].toUpperCase()];
    }
    if (newToken === undefined) {
      newToken = sub['index'][tokens[sub['token']].toLowerCase()];
    }
  }
  if (newToken === undefined) {
    let matchPattern;
    if (sub['useRegex']) {
      matchPattern = 'regex "' + regexStr + '"';
    }
    else {
      matchPattern = 'any value in the index';
    }
    console.log(
      'tried looking up ' + '"' + tokens[sub['token']] +'" in a table, '
      + 'but could not find a corresponding value'
    );
    if (('allowUnmatched' in sub) & sub['allowUnmatched']) {
      console.log("that's fine, since that lookup is optional");
      continue;
    }
    else {
      console.log("since that lookup was mandatory, no URL can be built");
      error_text = SUBSTITUTION_ERROR.replace('{schema}', schema.name);
      error_text = error_text.replace('{token}', sub['token']);
      throw Error(error_text);
    }
  }
  else {
    console.log(
      'looked up ' + sub['token'] + ' "' + tokens[sub['token']] 
      + '" in a table to set ' + outputToken + ' to "' + newToken + '"'
    );
    tokens[outputToken] = newToken;
  }
  }
  console.log(' ');
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
      console.log('omitted "'+part+'" because it has a placeholder');
    }
  }
  console.log('finished building URL: ' + url);
  return url;
}
