class PlayerSource:
  def __init__(self, display_name: str, path: str):
    self.display_name = str(display_name)
    self.path = str(path)

  def __eq__(self, o):
    """== operator overload"""

    # compare fields if string, can be used for search
    if isinstance(o, str):
      return o == self.path or o == self.display_name

    # else if not radio description don't even try
    if not isinstance(o, PlayerSource):
      raise NotImplementedError("Cannot compare PlayerSource with " + type(o).__name__)
      
    # compare strictly all the fields
    return self.path == o.path and self.display_name == o.display_name

  def after(self, player):
    return lambda *args, **kwargs: None

  def source(self):
    return None

  def __ne__(self, o):
    """!= oeprator overload"""
    return not self.__eq__(o)

  def __str__(self):
    """str() operator overload"""
    return "Nom: ``{0}``".format(self.display_name)