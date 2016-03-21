from django.utils.html import escape
from wagtail.utils.apps import get_app_submodules

from .shortcuts import get_rendition_or_not_found


class Format(object):
    def __init__(self, name, label, classnames, filter_spec):
        self.name = name
        self.label = label
        self.classnames = classnames
        self.filter_spec = filter_spec

    def editor_attributes(self, video, alt_text):
        """
        Return string of additional attributes to go on the HTML element
        when outputting this image within a rich text editor field
        """
        return 'data-embedtype="image" data-id="%d" data-format="%s" data-alt="%s" ' % (
            video.id, self.name, alt_text
        )

    def video_to_editor_html(self, image, alt_text):
        return self.image_to_html(
            image, alt_text, self.editor_attributes(image, alt_text)
        )

    def video_to_html(self, image, alt_text, extra_attributes=''):
        rendition = get_rendition_or_not_found(image, self.filter_spec)

        if self.classnames:
            class_attr = 'class="%s" ' % escape(self.classnames)
        else:
            class_attr = ''

        return '<img %s%ssrc="%s" width="%d" height="%d" alt="%s">' % (
            extra_attributes, class_attr,
            escape(rendition.url), rendition.width, rendition.height, alt_text
        )


FORMATS = []
FORMATS_BY_NAME = {}


def register_video_format(format):
    if format.name in FORMATS_BY_NAME:
        raise KeyError("Image format '%s' is already registered" % format.name)
    FORMATS_BY_NAME[format.name] = format
    FORMATS.append(format)


def unregister_video_format(format_name):
    global FORMATS
    # handle being passed a format object rather than a format name string
    try:
        format_name = format_name.name
    except AttributeError:
        pass

    try:
        del FORMATS_BY_NAME[format_name]
        FORMATS = [fmt for fmt in FORMATS if fmt.name != format_name]
    except KeyError:
        raise KeyError("Image format '%s' is not registered" % format_name)


def get_video_formats():
    search_for_video_formats()
    return FORMATS


def get_video_format(name):
    search_for_video_formats()
    return FORMATS_BY_NAME[name]


_searched_for_video_formats = False


def search_for_video_formats():
    global _searched_for_video_formats
    if not _searched_for_video_formats:
        list(get_app_submodules('video_formats'))
        _searched_for_video_formats = True


# Define default image formats
register_video_format(Format('fullwidth', 'Full width', 'richtext-image full-width', 'width-800'))
register_video_format(Format('left', 'Left-aligned', 'richtext-image left', 'width-500'))
register_video_format(Format('right', 'Right-aligned', 'richtext-image right', 'width-500'))