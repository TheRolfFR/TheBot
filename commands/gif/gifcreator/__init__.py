from PIL import Image

from .text_property import TextProperty
from PIL import ImageDraw

# url and download images
import requests
from io  import BytesIO

class GIFCreator:
  def __init__(self, background_color="#000000", width=200, height=200):
    self.background_color = background_color

    self.width = width
    self.height = height

    self.duration = 0

    self.index = 0

    self.images = [Image.new("RGBA", (self.width, self.height), self.background_color)]

  def nbFrames(self):
    return len(self.images)
  
  def resize(self, size):
    for i in range(0, self.nbFrames()):
      self.images[i] = self.images[i].resize(size, Image.BICUBIC)

  def image(self, index: int):
    if index < 0 or index >= self.nbFrames():
      raise ValueError("Incorrect index chosen")
    return self.images[index]

  def seek(self, index: int):
    if index < 0 or index >= self.nbFrames():
      raise ValueError("Incorrect index chosen")

    self.index = index

  def paste(self, other, pos):
    other_images_array = []
    if isinstance(other, GIFCreator):
      # easier because just copy frames
      for i in range(other.nbFrames()):
        other_images_array.append(other.image(i).copy())

      # copy max duration
      self.duration = max(self.duration, other.duration)
    elif "copy" in dir(other):
      try:
        nb_frames = other.n_frames

        for i in range(0, nb_frames):
          other.seek(i)
          other_images_array.append(other.copy())

        # copy max duration
        self.duration = max(self.duration, other.info.get("duration", 0))
      except:
        other_images_array.append(other.copy())
    else:
      raise ValueError("Incorect other image")

    # now paste to our images except last one
    for i in range(min(len(other_images_array), self.nbFrames() - 1)):
      self.images[i].paste(other_images_array[i], pos)

    # copy last image
    last_image_copy = self.images[self.nbFrames() - 1].copy()

    # paste other image on our last image
    if len(other_images_array) >= self.nbFrames():
      self.images[self.nbFrames() - 1].paste(other_images_array[self.nbFrames() - 1], pos)

    # for other images images left, append new images to our array
    for i in range(self.nbFrames(), len(other_images_array)):
      self.images.append(last_image_copy.copy())
      self.images[self.nbFrames() - 1].paste(other_images_array[i], pos)

  def addText(self, text_properties: TextProperty, x: int, y:int, text):
    d = self.draw()

    text_properties.render(self.images[self.index], d, x, y, text)
    return

  def draw(self):
    return ImageDraw.Draw(self.images[self.index], "RGBA")

  def toBuffer(self):
    buffered = BytesIO()

    if len(self.images) > 1:
      self.images[0].save(buffered, format='GIF', save_all=True, append_images=self.images[1:], optimize=False, loop=0, duration=self.duration)
    else:
      self.images[0].save(buffered, format="PNG")
    
    buffered.seek(0)

    return buffered

  @staticmethod
  def loadImageFromURL(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

  @staticmethod
  def loadImageFromPath(path):
    return Image.open(path)
