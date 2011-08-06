# genson_parser.py
#
# Based on json parser code from Paul McGuire, 2007
#
#
genson_bnf = """
object 
    { members } 
    {} 
key
    string
    key_tuple
key_tuple
    ( key_list )
key_list
    string
    key_list, string
members 
    key : value 
    members , key : value
value_tuple
    ( elements )
    ()
array 
    [ elements ]
    [] 
elements 
    value 
    elements , value
generator
    kw ()
    kw (args)
    kw (kwargs)
    kw (args, kwargs)
args
    elements
kwargs
    kw = value
    kwargs , kw = value
value 
    string
    number
    object
    array
    true
    false
    value_tuple
    null
"""

from pyparsing import *
from parameter_generators import *

# a simple helper functions
def generator(name, gen_args=[], gen_kwargs={}):

    generator_class = generators.get(name, None)
    if generator_class is None:
        raise Exception('Unknown generator class: %s' % name)
    
    if type(gen_kwargs) is ParseResults:
        gen_kwargs = gen_kwargs.asList()
    gen_kwargs = dict(gen_kwargs)
    
    g = generator_class(*gen_args, **gen_kwargs)
    
    return g

TRUE = Keyword("true").setParseAction( replaceWith(True) )
FALSE = Keyword("false").setParseAction( replaceWith(False) )
NULL = Keyword("null").setParseAction( replaceWith(None) )

json_string = dblQuotedString.setParseAction( removeQuotes )
json_number = Combine( Optional('-') + ( '0' | Word('123456789',nums) ) +
                    Optional( '.' + Word(nums) ) +
                    Optional( Word('eE',exact=1) + Word(nums+'+-',nums) ) )

genson_key_tuple = Forward()
genson_key = ( json_string | genson_key_tuple )
genson_key_tuple << Suppress('(') + delimitedList( genson_key ) + \
                         Suppress(')')
genson_key_tuple.setParseAction(tuple)

json_object = Forward()
json_value = Forward()
json_elements = delimitedList( json_value )
json_array = Group(Suppress('[') + Optional(json_elements) + Suppress(']') )

genson_value_tuple = Suppress('(') + json_elements + Suppress(')')
genson_value_tuple.setParseAction(tuple)

genson_kwargs = Group(delimitedList( Word(alphas) + Suppress("=") + \
                              json_value ))
genson_generator =  Word(alphas)("name") + \
                    Suppress('(') + \
                    Optional(json_elements)("args") + \
                    Optional(Suppress(',')) +\
                    Optional(genson_kwargs)("kwargs") + \
                    Suppress(')') 
genson_generator.setParseAction(lambda x: generator(x.name, x.args, x.kwargs))

genson_grid_shorthand = Suppress("<") + \
                       json_elements("args") + \
                       Suppress(">") 
genson_grid_shorthand.setParseAction(lambda x: generator("grid", x.args))

json_value << ( genson_value_tuple | genson_generator | \
                genson_grid_shorthand | \
                json_string | json_number | json_object | \
                json_array | TRUE | FALSE | NULL )

member_def = Group( genson_key + Suppress(':') + json_value )
json_members = delimitedList( member_def )
json_object << Dict( Suppress('{') + Optional(json_members) + Suppress('}') )

json_comment = cppStyleComment 
json_object.ignore( json_comment )

def clean_dict(x):
    x_list = x.asList()
    return dict(x_list)

json_object.setParseAction(clean_dict)

def convert_numbers(s,l,toks):
    n = toks[0]
    try:
        return int(n)
    except ValueError, ve:
        return float(n)
        
json_number.setParseAction( convert_numbers )
    
class GENSONParser:
    def __init__(self):
        self.grammar = json_object
    
    def parse_string(self, genson_string):
        result = self.grammar.parseString(genson_string)
        return result.asList()[0]
