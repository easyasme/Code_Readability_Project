'''
A wrapper for expression functions that makes optional use of 'order' and 'delta' 
specifications. Multiple outputs are supported for non-symbolic expressions. Note
that an expression may comprise a constant by not being callable, and therefore 
not all expressions are functions.
'''
import types
import collections
import functools
import sympy
from probayes.vtypes import isscalar
from probayes.icon import isiconic
from probayes.expr import Expr

#-------------------------------------------------------------------------------
def islambda(func):
  if not callable(func):
    return False
  if type(func) is types.LambdaType:
    return func.__name__ == '<lambda>'

#-------------------------------------------------------------------------------
class Expression:
  """ A expression wrapper to enable object representations as an uncallable
  array, a callable function, or a tuple/dict of callable functions

  :example:
  >>> from probayes.expression import Expression
  >>> hw = Expression("Hello World!")
  >>> print(hw())
  Hello World!
  >>> inc = Expression(lambda x: x+1)
  >>> print(inc(2.))
  3.0
  >>> inc_dec = Expression( (lambda x:x+1, lambda x:x-1) )
  >>> print(inc_dec[0](3.))
  4.0
  >>> print(inc_dec[1](3.))
  2.0
  >>> sqr_sqrt = Expression( {'sqr': lambda x:x**2, 'sqrt': lambda x:x**0.5} )
  >>> print(sqr_sqrt['sqr'](3.))
  9.0
  >>> print(sqr_sqrt['sqrt'](4.))
  2.0

  Since multiple expressions are supported, the symbolic value of Expression
  is not related to the input.
  """

  # Protected
  _expr = None     # Expression set
  _args = None     # Optional args
  _kwds = None     # Optional kwds
  _exprs = None    # Dict of iconic Expr objects
  _partials = None # Dict of partial functions
  _keys = None     # Keys of partials
  _ismulti = None  # Flag to denote multiple expression
  _callable = None # Flag to denote callable expression
  _islambda = None # Flag to denote lambda callable
  _isscalar = None # Flag to denote uncallable scalar
  _isiconic = None # Flag to denote sympy expression
  _symbols = None  # Dict of iconic symbols used

  # Private
  __invertible = None
  __inverse = None
  __invexpr = None
  __derinv = None # derivative of value with respect to inverse
  __order = None
  __delta = None

#-------------------------------------------------------------------------------
  def __init__(self, expr=None, *args, **kwds):
    """ Initialises instances according to object in expr, which may be an 
    uncallable object, a callable function, or a tuple of callable functions. 
    See set_expr()
    """
    self.set_expr(expr, *args, **kwds)
    
#-------------------------------------------------------------------------------
  @property
  def expr(self):
    return self._expr

  @property
  def args(self):
    return self._args

  @property
  def kwds(self):
    return self._kwds

  @property
  def order(self):
    return self.__order

  @property
  def delta(self):
    return self.__delta

  @property
  def callable(self):
    return self._callable

  @property
  def islambda(self):
    return self._islambda

  @property
  def ismulti(self):
    return self._ismulti

  @property
  def isscalar(self):
    return self._isscalar

  @property
  def isiconic(self):
    return self._isiconic

  @property
  def inverse(self):
    return self.__inverse

  @property
  def invexpr(self):
    return self.__invexpr

  @property
  def derinv(self):
    return self.__derinv

  @property
  def invertible(self):
    return self.__invertible

  @property
  def keys(self):
    return self._keys

  @property
  def symbols(self):
    return self._symbols

  def set_expr(self, expr=None, *args, **kwds):
    """ Set the Func instance's function object.

    :param expr: an uncallable object, callable function, or tuple of functions
    :param *args: arguments to pass onto callables
    :param **kwds: keywords to pass onto callables

    Note that the following two reserved keywords are disallowed:

    'order': which instead denotes a dictionary of remappings.
    'delta': which instead denotes a mapping of differences.
    """
    self._expr = expr
    self._args = tuple(args)
    self._kwds = dict(kwds)
    self._callable = None
    self._islambda = None
    self._ismulti = None
    self._isscalar = None
    self._isiconic = None
    self.__order = None
    self.__delta = None
    self.__inverse = None
    self.__invexpr = None
    self.__invderi = None
    self.__invertible = False if 'invertible' not in kwds else \
                        self._kwds.pop('invertible')
    self._exprs = collections.OrderedDict()
    self._symbols = collections.OrderedDict()

    # Sanity check func
    if self._expr is None:
      assert not args and not kwds, "No optional args without a function"
    self._isscalar = isscalar(self._expr)
    self._isiconic = isiconic(self._expr)
    self._ismulti = isinstance(self._expr, (dict, tuple))
    if self.__invertible:
      assert not self._ismulti,\
          "Cannot invert for multiple expressions"

    # Non-multi iconic
    if self._isiconic:
      self._exprs.update({None: Expr(self._expr, *self._args, **self._kwds)})
      self._symbols.update(self._exprs[None].symbols)
      self._ismulti = self.__invertible and \
                      len(self._exprs[None].symbols) == 1
      self._callable = True
      self._islambda = False

    # Unitary
    elif not self._ismulti:
      self._callable = callable(self._expr)
      self._islambda = islambda(self._expr)
      if not self._callable:
        assert not args and not kwds, \
            "No optional arguments with uncallable expressions"
        self._isscalar = isscalar(self._expr)

    # Multi
    else:
      exprs = self._expr if isinstance(self._expr, tuple) else \
              self._expr.values()
      self._callable = False
      self._islambda = False
      self._isscalar = False
      self._isiconic = False
      each_callable = [callable(expr) for expr in exprs]
      each_islambda = [islambda(expr) for expr in exprs]
      each_isscalar = [isscalar(expr) for expr in exprs]
      each_isiconic = [isiconic(expr) for expr in exprs]
      assert len(set(each_callable)) < 2, \
          "Cannot mix callable and uncallable expressions"
      assert len(set(each_islambda)) < 2, \
          "Cannot mix lambda and non-lambda expressions"
      assert len(set(each_isscalar)) < 2, \
          "Cannot mix scalars and nonscalars"
      assert len(set(each_isiconic)) < 2, \
          "Cannot mix iconics and non-iconics"
      if len(self._expr):
        self._callable = each_callable[0]
        self._islambda = each_islambda[0]
        self._isscalar = each_isscalar[0]
        self._isiconic = each_isiconic[0]
      if not self._callable:
        assert not args and not kwds, "No optional args with uncallable function"
      if self._isiconic:
        assert not args and not kwds, "No optional args with iconic function"
      if self._isiconic:
        if isinstance(self._expr, tuple):
          for i, expr in enumerate(self._expr):
            self._exprs.update({i: Expr(expr, *self._args, **self._kwds)})
            self._symbols.update(self._exprs[i].symbols)
        elif isinstance(self._expr, dict):
          for key, val in self._expr.items():
            self._exprs.update({key: Expr(val, *self._args, **self._kwds)})
            self._symbols.update(self._exprs[key].symbols)
    if 'order' in self._kwds:
      self.set_order(self._kwds.pop('order'))
    if 'delta' in self._kwds:
      self.set_delta(self._kwds.pop('delta'))
    self._set_partials()
    self._keys = list(self._partials.keys())

#-------------------------------------------------------------------------------
  def set_order(self, order=None):
    """ Sets an order remapping dictionary for functional calls in which
    keyword arguments are mapped to position (in numeric) or rekeyed (if str).
    """
    self.__order = order
    if self.__order is None:
      return
    assert self.__delta is None, "Cannot set both order and delta"
    self._check_mapping(self.__order)

#-------------------------------------------------------------------------------
  def set_delta(self, delta=None):
    """ Sets a difference remapping dictionary for functional calls in which
    keyword arguments are mapped to position (in numeric) or rekeyed (if str).
    """
    self.__delta = delta
    if self.__delta is None:
      return
    assert self.__order is None, "Cannot set both order and delta"
    assert not self.isiconic, "Cannot set delta when using symbols"
    self._check_mapping(self.__delta)

#-------------------------------------------------------------------------------
  def _check_mapping(self, mapping=None):
    """ Perform sanity checkings on mapping dictionary """
    if mapping is None:
      return
    # Used to sanity-check mapping dicts e.g. order and delta
    assert isinstance(mapping, dict), \
        "Mapping must be a dictionary type, not {}".format(type(mapping))
    if self.isiconic:
      assert not any(list(mapping.values())), \
          "Cannot remap for iconic expressions"
    key_list = list(mapping.keys())
    ind_list = list(mapping.values())
    keys = []
    inds = []
    for key, ind in zip(key_list, ind_list):
      keys.append(key)
      if type(ind) is int:
        inds.append(ind)
      elif ind is None:
        pass
      elif not isinstance(ind, str):
        raise TypeError("Cannot interpret index specification value: {}".ind)
    indset = set(inds)
    if len(indset):
      assert indset == set(range(min(indset), max(indset)+1)), \
          "Index specification non_sequitur: {}".format(indset)

#-------------------------------------------------------------------------------
  @property
  def partials(self):
    return self._partials

  def _set_partials(self):
    # Protected function to update partial function dictionary of calls
    self._partials = collections.OrderedDict()

    # Iconic partials calls are set to Expr.__call__
    if self._isiconic:
      if not self._ismulti or self.__invertible:
        call = functools.partial(Expr.__call__, self._exprs[None])
        self._partials.update({None: call})

        # If invertible, solve the expression
        if self.__invertible:
          self._partials.update({0: call})
          expr = self._exprs[None]
          key = list(expr.symbols.keys())[0]
          derinv = sympy.Derivative(expr, self._exprs[None].symbols[key]).doit()
          self.__derinv = Expr(derinv)
          inv_key = "_{}_inv".format(key)
          self.__inverse = sympy.Symbol(inv_key)
          invexprs = sympy.solve(self._expr - self.__inverse, self._exprs[None].symbols[key])
          n_exprs = len(invexprs)
          assert n_exprs, "No invertible solutions for expression {}".format(
              self._expr)
          invexpr = invexprs[0]
          if n_exprs > 1:
            for expr in invexprs[1:]:
              if len(expr.__repr__()) < len(invexpr.__repr__()):
                invexpr = expr
          self.__invexpr = Expr(invexpr)
          call = functools.partial(Expr.__call__, self.__invexpr)
          self._partials.update({1: call})
          self._partials.update({-1: call})
      else:
        if isinstance(self._exprs, tuple):
          for i, expr in enumerate(self._exprs):
            call = functools.partial(Expr.__call__, expr)
            self._partials.update({i: call})
          self._partials.update({-1: call})
        elif isinstance(self._exprs, dict):
          for key, val in self._exprs.items():
            call = functools.partial(Expr.__call__, val)
            self._partials.update({key: call})

    # Non-multiples are keyed by: None
    elif not self._ismulti:
      if self._isiconic:
        call = functools.partial(Expr.__call__, self)
        self._partials.update({None: call})
      else:
        call = functools.partial(Expression._partial_call, self, self._expr, 
                                 *self._args, **self._kwds)
        self._partials.update({None: call})

    # Tuples are keyed by index
    elif isinstance(self._expr, tuple):
      for i, expr in enumerate(self._expr):
        call = functools.partial(Expression._partial_call, self, expr, 
                                 *self._args, **self._kwds)
        self._partials.update({i: call})
      self._partials.update({-1: call})

    # Dictionaries keys are mapped directly
    elif isinstance(self._expr, dict):
      for key, val in self._expr.items():
        call = functools.partial(Expression._partial_call, self, val, 
                                 *self._args, **self._kwds)
        self._partials.update({key: call})
    else:
      raise TypeError("Unknown expression type: {}".format(type(self._expr)))
    self._keys = list(self._partials.keys())

#-------------------------------------------------------------------------------
  def _call(self, expr=None, *args, **kwds):
    """ Private call used by the wrapped Func interface that is _ismulti-blind.
    (see __call__ and __getitem__).
    """
    assert not self._isiconic, \
        "Iconic calls must be handled by Expr() objects"
    #argsin = args; kwdsin = kwds; import pdb; pdb.set_trace() # debugging

    # Non-callables
    if not self._callable:
      assert not args and not kwds, \
          "No optional args with uncallable or symbolic expressions"
      if self._ismulti:
        return expr
      if expr is None:
        expr = self._expr
      return expr

    # Allow first argument to denote kwds
    if len(args) == 1 and isinstance(args[0], dict):
      args, kwds = (), {**kwds, **dict(args[0])}
    #argsmid = args; kwdsmid = kwds; import pdb; pdb.set_trace() # debugging

    # Callables with neither order nor delta are straightforwards
    if not self.__order and not self.__delta:
      if self._islambda and hasattr(expr, '__code__') and \
          not expr.__code__.co_argcount: # Allow argument-free lambdas
        assert not len(args), \
            "Unexpected entering of positional arguments: {}".format(args)
        return expr()
      elif args or all(isinstance(key, str) for key in kwds.keys()):
        return expr(*args, **kwds)
      else:
        return expr(dict(kwds))

    # Append None to args according to mapping index specification
    n_args = len(args)
    mapping = self.__order or self.__delta
    for val in mapping.values():
      if type(val) is int:
        n_args = max(n_args, val+1)
    args = list(args)
    while len(args) < n_args:
      args.append(None)

    # Callables with order wrapper
    if self.__order:
      for key, val in self.__order.items():
        if type(val) is int:
          args[val] = kwds.pop(key)
        elif val is None:
          kwds.pop(key)
        elif isinstance(val, str):
          kwds.update({val: kwds.pop(key)})
        else:
          raise TypeError("Unrecognised order key: val type: {}:{}".\
                          format(key, val))
      return expr(*tuple(args), **kwds)

    # Callables with delta wrapper
    for key, val in self.__delta.items():
      if key[-1] != "'":
        value = kwds.pop(key)
      else:
        value = kwds.pop(key) - kwds.pop(key[:-1])
      if type(val) is int:
        args[val] = value
      elif val is None:
        pass
      elif isinstance(val, str):
        kwds.update({val: value})
      else:
        raise TypeError("Unrecognised delta key: val type: {}:{}".\
                        format(key, val))

    #argsout = args; kwdsout = kwds; import pdb; pdb.set_trace() # debugging
    return expr(*tuple(args), **kwds)

#-------------------------------------------------------------------------------
  def _partial_call(self, *args, **kwds):
    return self._call(*args, **kwds)

#-------------------------------------------------------------------------------
  def __call__(self, *args, **kwds):
   """ Wrapper call to the function with optional inclusion of additional
   args and kwds. """
   assert not self._ismulti, \
       "Cannot call with multiple expression, use Expression[{}]()".format(
           list(self._keys()))
   return self._partials[None](*args, **kwds)

#-------------------------------------------------------------------------------
  def __getitem__(self, arg):
   r""" Returns the $i$th function from the expr tuple where if is $i$ is
   numeric, otherwise arg is treated as key returning the corresponding
   value in the expr dictionary. """
   if arg is not None: 
     assert self._ismulti, \
         "Cannot call with non-multiple expression, use Expression()"
   if isinstance(arg, slice):
     if arg == slice(None):
       return self._expr
   if isinstance(arg, (tuple, list)) and not len(arg):
     if isinstance(arg, tuple):
       return self._partials
     return self._partials[None]
   return self._partials[arg]

#-------------------------------------------------------------------------------
  def __len__(self):
    """ Returns the number of expressions in the tuple set by set_expr() """
    if not self._ismulti:
      return None
    return len(self._partials)

#-------------------------------------------------------------------------------
  def __repr__(self):
    """ Print representation """
    if self._isiconic or not self._callable:
      return object.__repr__(self)+ ": '{}'".format(self._expr)
    if self._keys is None:
      return object.__repr__(self) 
    return object.__repr__(self)+ ": '{}'".format(self._keys)

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
if __name__ == "__main__":
  import doctest
  doctest.testmod()

#-------------------------------------------------------------------------------
