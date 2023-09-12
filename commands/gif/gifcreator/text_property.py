import re
from PIL import Image
from PIL import ImageFont, ImageDraw, ImageOps

# url and download emojis
import requests
from io import BytesIO

EMOJI_REGEX = re.compile("(<:[^:]+:([0-9]+)>)")


def _emoji_size(fontSize):
    return int(fontSize * 22 / 16)


def _drawLine(
    img: Image.Image,
    d: ImageDraw,
    offsetX: int,
    offsetY: int,
    line: str,
    font: ImageFont,
    fontSize,
    emojiDict: dict,
    stroke_width: int,
    stroke_fill: tuple,
):
    # find emojis
    emojis = EMOJI_REGEX.findall(line)

    emojiSize = _emoji_size(fontSize)

    bbox = font.getbbox("EXAMPLE")
    lineWidth = bbox[2] - bbox[0]
    lineHeight = bbox[3] - bbox[1]

    # split line by emojis, really complicated because we need everything
    linearr = []
    linelast = line
    if len(emojis):
        for i in range(len(emojis)):
            explode = linelast.split(emojis[i][0], 1)
            linelast = explode[1]
            linearr.append(explode[0])  # add first part
            linearr.append(int(emojis[i][1]))  # add emoji number after

    # else there is no emoji just append the line or lastline
    linearr.append(linelast)

    # draw
    for element in linearr:
        if isinstance(element, int):
            if not element in emojiDict:
                # load emoji
                response = requests.get(
                    "https://cdn.discordapp.com/emojis/" + str(element) + ".png"
                )
                ori = Image.open(BytesIO(response.content))
                orisize = ori.size
                finalSize = (
                    int(orisize[0] / max(orisize) * emojiSize),
                    int(orisize[1] / max(orisize) * emojiSize),
                )
                emojiDict[element] = ori.resize(finalSize, Image.BICUBIC)

            # paste emoji
            img.paste(
                emojiDict[element], (int(offsetX), int(offsetY)), emojiDict[element]
            )
            offsetX += emojiSize
        else:
            # it's text
            bbox = font.getbbox(element)
            lineWidth = bbox[2] - bbox[0]
            lineHeight = bbox[3] - bbox[1]
            d.text(
                (offsetX, offsetY),
                element,
                font=font,
                stroke_width=stroke_width,
                stroke_fill=stroke_fill,
            )
            offsetX += lineWidth

    return (
        offsetY + (max(emojiSize, lineHeight) if len(emojis) else lineHeight),
        emojiDict,
    )


class TextProperty:
    def __init__(self, stroke_width=0, stroke_fill=None, **kwargs):
        self.backgroundColor = (
            kwargs["backgroundColor"] if "backgroundColor" in kwargs else None
        )

        self.fontPath = kwargs["fontPath"]
        self.fontSize = kwargs["fontSize"]

        self.color = kwargs["color"]

        self.backgroundMargin = (
            kwargs["backgroundMargin"] if "backgroundMargin" in kwargs else 0
        )

        self.alignment = kwargs["alignment"] if "alignment" in kwargs else "left"

        _preload_font = kwargs["preloadFont"] if "preloadFont" in kwargs else False
        self.font = None
        self.realFontSize = None

        self.boxSize = kwargs["boxSize"] if "boxSize" in kwargs else (-1, -1)

        self.stroke_width = stroke_width
        self.stroke_fill = stroke_fill

        if _preload_font:
            self.preloadFont()

    def computeFontSize(self):
        return self.fontSize

    def preloadFont(self):
        self.realFontSize = self.computeFontSize()
        self.font = self.loadFont(self.fontPath, self.realFontSize)

    def loadFont(self, path: str, size: float):
        if self.font is None:
            if path.endswith("ttf"):
                return ImageFont.truetype(path, size)
            return ImageFont.load_default()

        return self.font

    def computeSize(self, draw, text: str):
        """Computes size of render"""
        lines = text.split("\\n")

        _font_size = self.computeFontSize()
        _font = self.loadFont(self.fontPath, _font_size)

        height = 0
        maxWidth = 0

        emojiSize = _emoji_size(_font_size)

        for line in lines:
            # find emojis
            emojis = EMOJI_REGEX.findall(line)

            # create a pure line
            pureLine = line
            for emojiMatch in emojis:
                pureLine = pureLine.replace(
                    emojiMatch[0], ""
                )  # remove da fuck out of the line

            bbox = _font.getbbox(pureLine)
            lineWidth = bbox[2] - bbox[0]
            lineHeight = bbox[3] - bbox[1]

            # you need to take into account the emojis width
            lineWidth += emojiSize * len(emojis)

            maxWidth = max(maxWidth, lineWidth)
            height += (
                max(emojiSize, lineHeight) if len(emojis) else lineHeight
            )  # get max if emojis present in line

        return (maxWidth, height)

    def render(self, img: Image.Image, draw: ImageDraw, x: int, y: int, text: str):
        lines = text.split("\\n")

        if self.font is None:
            self.preloadFont()

        _emoji_dict = {}
        _font_size = self.computeFontSize()

        entire_size = self.computeSize(draw, text)

        for line in lines:
            (line_width, line_height) = self.computeSize(draw, line)

            if self.alignment == "center":
                x = x - int(entire_size[0] / 2)

            # draw background
            if self.backgroundColor is not None:
                draw.rectangle(
                    (
                        x - self.backgroundMargin,
                        y - self.backgroundMargin,
                        x + line_width + 2 * self.backgroundMargin,
                        y + line_height + 2 * self.backgroundMargin,
                    ),
                    self.backgroundColor,
                )

            # draw text
            (y, _emoji_dict) = _drawLine(
                img,
                draw,
                x,
                y,
                line,
                self.font,
                self.realFontSize,
                _emoji_dict,
                self.stroke_width,
                self.stroke_fill,
            )
        return
