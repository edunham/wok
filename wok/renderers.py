import logging
from wok import util

# Check for pygments
try:
    import pygments
    have_pygments = True
except ImportError:
    logging.warn('Pygments not enabled.')
    have_pygments = False

# List of available renderers
all = []

def factory(filename):
    ext = filename.split('.')[-1]
    for r in all:
        for e in r.extensions:
            if ext == e:
                if r == ReStructuredText:
                    return r(filename)
                else:
                    return r()
    logging.warning('No parser found for {0}. '
        'Using default renderer.'.format(filename))
    return Renderer() # no matches found, return default

class Renderer(object):
    extensions = []

    def render(self, plain):
        return plain
all.append(Renderer)

class Plain(Renderer):
    """Plain text renderer. Replaces new lines with html </br>s"""
    extensions = ['txt']

    def render(self, plain):
        return plain.replace('\n', '<br>')
all.append(Plain)

# Include markdown, if it is available.
try:
    from markdown import markdown

    class Markdown(Renderer):
        """Markdown renderer."""
        extensions = ['markdown', 'mkd', 'md']

        plugins = ['def_list', 'footnotes']
        if have_pygments:
            plugins.extend(['codehilite(css_class=codehilite)', 'fenced_code'])

        def render(self, plain):
            return markdown(plain, Markdown.plugins)

    all.append(Markdown)

except ImportError:
    logging.warn("markdown isn't available, trying markdown2")
    markdown = None

# Try Markdown2
if markdown is None:
    try:
        import markdown2
        class Markdown2(Renderer):
            """Markdown2 renderer."""
            extensions = ['markdown', 'mkd', 'md']

            extras = ['def_list', 'footnotes']
            if have_pygments:
                extras.append('fenced-code-blocks')

            def render(self, plain):
                return markdown2.markdown(plain, extras=Markdown2.extras)

        all.append(Markdown2)
    except ImportError:
        logging.warn('Markdown not enabled.')


# Include ReStructuredText Parser, if we have docutils
try:
    import docutils.core
    from docutils.writers.html4css1 import Writer as rst_html_writer
    from docutils.parsers.rst import directives

    if have_pygments:
        from wok.rst_pygments import Pygments as RST_Pygments
        directives.register_directive('Pygments', RST_Pygments)

    class ReStructuredText(Renderer):
        """reStructuredText renderer."""
        extensions = ['rst']

        def __init__(self, source_path=None):
            self.source_path=source_path

        def render(self, plain):
            w = rst_html_writer()
            return docutils.core.publish_parts(plain, source_path=self.source_path, writer=w)['body']

    all.append(ReStructuredText)
except ImportError:
    logging.warn('reStructuredText not enabled.')


# Try Textile
try:
    import textile
    class Textile(Renderer):
        """Textile renderer."""
        extensions = ['textile']

        def render(self, plain):
            return textile.textile(plain)

    all.append(Textile)
except ImportError:
    logging.warn('Textile not enabled.')


if len(all) <= 2:
    logging.error("You probably want to install either a Markdown library (one of "
          "'Markdown', or 'markdown2'), 'docutils' (for reStructuredText), or "
          "'textile'. Otherwise only plain text input will be supported.  You "
          "can install any of these with 'sudo pip install PACKAGE'.")
