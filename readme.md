## GENSON

GENSON is a simple experimental extension to JSON syntax for specifying collections of JSON objects sampled from arbitrary spaces.  The primary use case for such a tool would be performing parameter searches / optimization, where each parameter set is allowed to be arbitrarily structured data.  Did I mention it was experimental?  It's only a few hundred lines of code, and I'm still feeling around for the right level of complexity.

The API is roughly meant to follow that of the Python `simplejson` module.  You can load a GENSON document from a file by calling `genson.load(f)`, and from a string by calling `genson.loads(s)`.  The returned object is an iterator over dictionary objects suitable for dumping as JSON (e.g. using `simplejson`).

GENSON is a strict superset of JSON, insofar as every JSON object is a valid GENSON object that resolves to itself. Additional syntax in GENSON allows for compactly specifying the generation of many JSON objects according to various sampling rules.  For instance,

    { 'parameter1': gaussian(0, 1, draws=6) }

resolves to six objects with `parameter1` draw from a zero mean, unit variance gaussian distribution.  Furthermore,

    { 'parameter2': < 1, 2, 3 > }
    
resolves to three objects with `parameter2` equal to 1, 2, and 3.  Combinations of sampling operations result in exhaustive crosses, such that

    { 'parameter3': <1, 2, 3>,
      'parameter4': <4, 5, 6> }

results in nine objects.

GENSON also introduces tuple keys to JSON as a mechanism for specifying sampling dependencies:

    { ('p6','p7','p8'): < (1,2,3), (4,5,6) > }

produces two objects, wherein the first `p6`, `p7`, and `p8` are equal to 1,2 and 3, and in the second they are equal to 4,5, and 6, respectively.

As in JSON, values can be arbitrarily deeply nested, such that constructs like:

    { ('p1', 'p2') : < ( uniform(-1,1), 4), ({"nested":"dictionary"}, 6)> }

are valid, and do what you'd "expect".

## Future plans

I'd like to add support for expressions and internal references, so that one key can refer to another (e.g. if you wanted a `threshold2` member to always be equal to `2*threshold1`).  This shouldn't be too hard; currently the parser is only about 100 lines long, and not terribly complex.