# python standard imports
import re
from copy import copy


class TokenOperation:
    """A function to perform a predefined string manipulation"""
    def __init__(
        self,
        action: str,
        data,
        mandatory: bool = True,
        token: str = None,
        output: str = None,
    ):
        """
        Arguments:
            action: The kind of string manipulation that this operation
                will perform, using the given data. There are a few
                different options:
                
                'sub': Regex substitution to perform on the text. Needs
                    a list of two values: [PATTERN, REPLACEMENT]
                
                'lookup': Check if the token matches any of the given
                    regexes (via case-insensitive matching), and if so,
                    replace it with the corresponding value. Needs a
                    dictionary of `regex`: `replacement` pairs.
                
                'case': Capitalize the token in the specified way.
                    Options are 'upper', 'lower', and 'title'.
                
                'lpad': Left pad the token with zeros until it is the
                    specified number of characters long. Requires an
                    int specifying the number of characters. You can
                    also specify the padding character by providing a
                    tuple: (MINIMUM_LENGTH, PADDING_CHARACTER).
                
                'number_style': Assume that the token is a number,
                    either in the form of digits, Roman numerals, or
                    number words like "thirty-seven". Convert it into
                    the specified number format, which can be any of
                    these:
                    
                    'cardinal', e.g. "twenty-seven"
                    
                    'cardinal spaced', e.g. "twenty seven"
                    
                    'cardinal unspaced', e.g. "twentyseven"
                    
                    'ordinal', e.g. "twenty-seventh"
                    
                    'ordinal spaced', e.g. "twenty seventh"
                    
                    'ordinal unspaced', e.g. "twentyseventh"
                    
                    'roman numeral', e.g. 'xxvii'
                    
                    'digit', e.g. '27'
                    
                    Note that number formatting only works for positive
                    whole numbers that do not exceed 40.
                
            data: any data that a given action needs specified, as
                described above
            
            mandatory: whether a failed lookup or format action should
                invalidate the entire citation
            
            token: Necessary for operations in StringBuilders. This
                value lets you provide the name of input token to use,
                allowing you to then use the modify_dict() method.
            
            output: If this value is set, modify_dict() will save the
                operation's output to the dictionary key with this name
                instead of modifying the input token in place.
        """
        if action == 'sub':
            self.func = lambda x: re.sub(data[0], data[1], x)
        elif action == 'lookup':
            table = {
                re.compile(k, flags=re.I):v
                for k, v in data.items()
            }
            self.func = lambda x: self._lookup(x, table, mandatory)
        elif action == 'case':
            self.func = lambda x: self._set_case(x, data)
        elif action == 'lpad':
            self.func = lambda x: self._left_pad(x, data)
        elif action == 'number_style':
            action_options = ['cardinal', 'ordinal', 'roman', 'digit']
            if data not in action_options:
                raise SyntaxError(
                    f'{data} is not a valid number style. Valid options: '
                    f'{action_options}'
                )
            self.func = lambda x: self._number_style(x, data, mandatory)
        else:
            raise SyntaxError(
                f'{action} is not a defined token operation.'
            )
        
        self.action = action
        self.data = data
        self.mandatory = mandatory
        self.token = token
        self.output = output
    
    @classmethod
    def from_dict(cls, data: dict):
        "load a TokenOperation from a dictionary of values"
        operations = []
        for key in ['sub', 'lookup', 'case', 'lpad', 'number style']:
            value = data.get(key)
            if value:
                action = key.replace(' ', '_')
                action_data = value
                break
        mandatory = data.get('mandatory', True)
        token = data.get('token')
        output = data.get('output')
        return cls(action, action_data, mandatory, token, output)
    
    def to_dict(self) -> dict:
        "save this TokenOperation to a dictionary of values"
        output = {}
        for key in ['token', 'output']:
            if self.__dict__.get(key):
                output[key] = self.__dict__[key]
        output[self.action] = self.data
        if not self.mandatory:
            output['mandatory'] = False
        
        spaced_output = {k.replace('_', ' '):v for k, v in output.items()}
        
        return spaced_output
    
    def modify_dict(self, tokens: dict):
        """
        apply this operation to a dictionary of tokens,
        editing them as appropriate
        """
        if not tokens.get(self.token):
            return
        if self.output:
            tokens[self.output] = self.func(tokens[self.token])
        else:
            tokens[self.token] = self.func(tokens[self.token])
    
    def __call__(self, input_value):
        return self.func(input_value)
    
    def __repr__(self):
        return (
            f'TokenOperation(action="{self.action}", data="{self.data}"'
            + (f', mandatory=False' if not self.mandatory else '')
            + (f', token="{self.token}"' if self.token else '')
            + (f', output="{self.output}"' if self.output else '')
            + ')'
        )
    
    # ================ Token Processing Operations =================== #
    
    def _lookup(
        self,
        input: str,
        table: dict[re.Pattern, str],
        mandatory: bool=False,
    ) -> str:
        for pattern, repl in table.items():
            if pattern.fullmatch(input):
                return repl
        if mandatory:
            regexes = [r.pattern for r in table.keys()]
            raise SyntaxError(f'{input} could not be found in {table}')
        else:
            return input
    
    def _set_case(self, input: str, case: str) -> str:
        if case == 'upper':
            return input.upper()
        elif case == 'lower':
            return input.lower()
        elif case == 'title':
            return input.title()
    
    def _left_pad(self, input: str, min_length: int, pad_char='0'):
        diff = min_length - len(input)
        if diff > 0:
            return (pad_char*diff + input)
        return input
    
    def _number_style(self, input: str, form: str, throw_error: bool=False):
        if input.isnumeric():
            value = int(input)
        elif input[:-2].isnumeric(): # e.g. "2nd"
            value = int(input[:-2])
        else:
            input = input.lower()
            for i, row in enumerate(number_words):
                if input in row:
                    value = i + 1
                    break
            else:
                if throw_error:
                    raise SyntaxError(
                        f'{input} cannot be recognized as a number'
                    )
        if form == 'digit':
            return str(value)
        forms = ['roman', 'cardinal', 'ordinal']
        output = number_words[value - 1][forms.index(form)]
        if form == 'roman':
            return output.upper()
        return output


class TokenType:
    """
    These objects represent categories of tokens that might be found in
    a citation.
    
    Attributes:
        regex: A regular expression that matches the actual text of the
            token as found in any document, like the "42" in "42 USC §
            1983" or the "Fourteenth" in "The Fourteenth Amendment".
            This regex will automatically be enclosed in a named capture
            group and inserted into any of the template's match patterns
            wherever the token's name appears in curly braces.
        edits: Steps to normalize the token as captured in the regex
            into a value that is consistent across multiple styles.
        default: Set the token to this value if it is not found in the
            citation.
        severable: If two citations only differ based on this token,
            and only because one of the tokens extends longer than the
            other, e.g. "(b)(2)" and "(b)(2)(A)", then `severable` means
            that the former citation is thought to encompass the latter.
    """
    def __init__(
        self,
        regex: str = r'\d+',
        edits: list[TokenOperation] = [],
        default: str = None,
        severable: bool = False,
    ):
        self.regex = regex
        self.edits = edits
        self.default = default
        self.severable = severable
    
    @classmethod
    def from_dict(cls, name: str, data: dict):
        "load a TokenType from a dictionary of values"
        return cls(
            regex = data['regex'],
            default = data.get('default'),
            edits = [
                TokenOperation.from_dict(v)
                for v in data.get('edits', [])
            ],
            severable=data.get('severable', False)
        )
    
    def to_dict(self) -> dict:
        "save this TokenType to a dictionary for storage in YAML format"
        output = {'regex': self.regex}
        if self.edits:
            output['edits'] = [
                e.to_dict() for e in self.edits
            ]
        if self.default:
            output['default'] = self.default
        if self.severable:
            output['severable'] = True
        return output
    
    def normalize(self, token: str) -> str:
        if not token:
            return self.default
        for op in self.edits:
            token = op(token)
        return token
    
    def __str__(self):
        return self.regex
    
    def __repr__(self):
        norms = '[' + ', '.join([
            repr(n) for n in self.edits or []
        ]) + ']'
        return (
            f"TokenType(regex='{self.regex}'"
            + (f", default='{self.default}'" if self.default else '')
            + (f', edits={norms}' if self.edits else '')
            + ')'
        )


class StringBuilder:
    """
    A function to take a dictionary of values and use it to construct a
    piece of text from them. This is used for citation templates' name
    builders and URL builders. 
    
    Attributes:
        parts: A list of strings that will be concatenated to create the
            string. Parts may contain bracketed references to citations'
            token values as well as templates' metadata. If a part
            references a token whose value is not set, the part will be
            omitted from the created string.
        edits: A list of TokenOperations that will be performed on the
            provided tokens before the string is constructed. If the
            edits have `output` values, it is possible for them to
            define entirely new tokens for the sole purpose of building
            the string.
        defaults: A dictionary of default token values to use when not
            overwritten by the citation. Generally these are provided by
            the template's meta attribute.
    """
    def __init__(
        self,
        parts: list[str],
        edits: list[TokenOperation] = [],
        defaults: dict[str, str] = {}
    ):
        self.parts = parts
        self.edits = edits
        self.defaults = defaults
    
    @classmethod
    def from_dict(cls, data: dict):
        "load StringBuilder from dictionary of values"
        edits = [
            TokenOperation.from_dict(o)
            for o in data.get('edits', [])
        ]
        parts = data['parts']
        defaults = data.get('defaults') or {}
        return cls(parts, edits, defaults)
    
    def to_dict(self) -> dict:
        "save StringBuilder to a dictionary of values"
        output = {'parts': self.parts}
        if self.edits:
            output['edits'] = [op.to_dict() for op in self.edits]
        return output
    
    def __call__(
        self,
        tokens: dict[str, str],
    ) -> str:
        if self.defaults:
            defaults = copy(self.defaults)
            defaults.update(tokens)
            tokens = defaults
        else:
            tokens = copy(tokens)
        tokens = {k:v for k,v in tokens.items() if v}
        for op in self.edits:
            try:
                op.modify_dict(tokens)
            except SyntaxError: # token operation failed; just skip it
                pass
        string_parts = []
        for part in self.parts:
            try:
                string_parts.append(part.format(**tokens))
            except KeyError: # skip parts that reference a nonexistent token
                pass
            # if a mandatory TokenOperation failed, don't return a URL
            except SyntaxError:
                string_parts = []
                break
        t = copy(tokens)
        return ''.join(string_parts) or None
    
    def __repr__(self):
        return (
            f'StringBuilder(parts={self.parts}'
            + (f', edits={self.edits}' if self.edits else '')
            + (f', defaults={self.defaults}' if self.defaults else '')
            + ')'
        )



# The number_words list is needed for the
# 'number_style' token operation

number_words = [
    ('i', 'one', 'first'),
    ('ii', 'two', 'second'),
    ('iii', 'three', 'third'),
    ('iv', 'four', 'fourth'),
    ('v', 'five', 'fifth'),
    ('vi', 'six', 'sixth'),
    ('vii', 'seven', 'seventh'),
    ('viii', 'eight', 'eighth'),
    ('ix', 'nine', 'ninth'),
    ('x', 'ten', 'tenth'),
    ('xi', 'eleven', 'eleventh'),
    ('xii', 'twelve', 'twelfth'),
    ('xiii', 'thirteen', 'thirteenth'),
    ('xiv', 'fourteen', 'fourteenth'),
    ('xv', 'fifteen', 'fifteenth'),
    ('xvi', 'sixteen', 'sixteenth'),
    ('xvii', 'seventeen', 'seventeenth'),
    ('xviii', 'eighteen', 'eighteenth'),
    ('xix', 'nineteen', 'nineteenth'),
    ('xx', 'twenty', 'twentieth'),
    'xxi', 'xxii', 'xxiii', 'xxiv', 'xxv',
    'xxvi', 'xxvii', 'xxviii', 'xxix',
    ('xxx', 'thirty', 'thirtieth'),
    'xxxi', 'xxxii', 'xxxiii', 'xxxiv', 'xxxv',
    'xxxvi', 'xxxvii', 'xxxviii', 'xxxix',
    ('xL', 'forty', 'fortieth'),
]
for i, entry in enumerate(number_words):
    if type(entry) is tuple:
        tens_place = entry[1]
    else:
        digit = number_words[i % 10]
        number_words[i] = (
            entry,                      # roman numeral
            f'{tens_place}-{digit[1]}', # cardinal number
            f'{tens_place}-{digit[2]}', # ordinal number
        )
number_words = tuple(number_words)
