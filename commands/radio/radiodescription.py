class RadioDescription:
  display_name: str
  url: str
  aliases: list

  def __init__(self, display_name: str, url: str, aliases: list):
    self.display_name = str(display_name)
    self.url = str(url)
    self.aliases =  [str(x).lower() for x in aliases]

  def __eq__(self, o):
    """== operator overload"""

    # compare fields if string, can be used for search
    if isinstance(o, str):
      return o == self.url or o == self.display_name or o in self.aliases

    # else if not radio description don't even try
    if not isinstance(o, RadioDescription):
      raise NotImplementedError("Cannot compare RadioDescription with " + type(o).__name__)
      
    # compare strictly all the fields
    return self.url == o.url and self.display_name == o.display_name

  def __ne__(self, o):
    """!= oeprator overload"""
    return not self.__eq__(o)

  def __str__(self):
    """str() operator overload"""
    return "Nom: ``{0}``, Alias: ``{1}``".format(self.display_name, '``, ``'.join(self.aliases))