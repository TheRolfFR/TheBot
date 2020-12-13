class RadioDescription:
  display_name: str
  url: str
  aliases: list

  def __init__(self, display_name: str, url: str, aliases: list):
    self.display_name = display_name
    self.url = url
    self.aliases =  [x.lower() for x in aliases]

  def __eq__(self, o):
    """== operator overload"""
    if not isinstance(o, RadioDescription):
      return False
      
    return str(self.url) == str(o.url) and str(self.display_name) == str(o.display_name)

  def __ne__(self, o):
    """!= oeprator overload"""
    return not self.__eq__(o)

  def __str__(self):
    """str() operator overload"""
    return "Nom: ``{0}``, Alias: ``{1}``".format(self.display_name, '``, ``'.join(self.aliases))