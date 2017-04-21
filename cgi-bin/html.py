#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

attribute_names = dict(
    httpEquiv='http-equiv',
    className='class'
)


html_escapes = [(u'&', u'&amp;'),
                (u'>', u'&gt;'),
                (u'<', u'&lt;'),
                (u'"', u'&quot;'),
                (u"'", u'&apos;')]


def escape(string):
    for (x, y) in html_escapes:
        if x in string:
            string = string.replace(x, y)
    return string

class HtmlFragment():
    def __init__(self):
        self.children = []

    def append_child(self, child):
        self.children.append(child)

    def _create_element(self, tag, attrs, separate_closing_tag=True):
        result = HtmlElement(self.document(), tag, separate_closing_tag)
        self._hookup_to_parent(result)
        result.attr(**attrs)
        return result

    def html(self, **attrs):
        return self._create_element(u'html', attrs)

    def head(self, **attrs):
        return self._create_element(u'head', attrs)

    def body(self, **attrs):
        return self._create_element(u'body', attrs)

    def meta(self, **attrs):
        return self._create_element(u'meta', attrs, False)

    def link(self, **attrs):
        return self._create_element(u'link', attrs, False)

    def title(self, **attrs):
        return self._create_element(u'title', attrs)

    def script(self, **attrs):
        return self._create_element(u'script', attrs)

    def a(self, **attrs):
        return self._create_element(u'a', attrs)

    def p(self, **attrs):
        return self._create_element(u'p', attrs)

    def br(self, **attrs):
        return self._create_element(u'br', attrs, False)

    def ul(self, **attrs):
        return self._create_element(u'ul', attrs)

    def li(self, **attrs):
        return self._create_element(u'li', attrs)

    def iframe(self, **attrs):
        return self._create_element(u'iframe', attrs)

    def div(self, **attrs):
        return self._create_element(u'div', attrs)

    def span(self, **attrs):
        return self._create_element(u'span', attrs)

    def img(self, **attrs):
        return self._create_element(u'img', attrs, False)

    def text(self, txt):
        result = HtmlText(txt)
        self._hookup_to_parent(result)
        return result

    def innerhtml(self, html):
        result = HtmlSource(html)
        self._hookup_to_parent(result)
        return result

    def comment(self, txt):
        result = HtmlComment(txt)
        self._hookup_to_parent(result)
        return result

    # Utility functions
    def meta_utf8(self):
        self.meta(content='text/html, charset=utf-8', httpEquiv='Content-Type')

    def favicon(self, href):
        self.link(type='image/ico', rel='icon', href=href)

    def css(self, href):
        self.link(type='text/css', rel='stylesheet', href=href)

    def java_script(self, src):
        self.script(type='text/javascript', src=src)

    def print_on(self, stream):
        for child in self.children:
            child.print_on(stream)


class HtmlDocument(HtmlFragment):
    def __init__(self):
        HtmlFragment.__init__(self)
        self.stack = [self]

    def document(self):
        return self

    def _hookup_to_parent(self, child):
        self.document().stack[-1].append_child(child)

    def print_on(self, stream):
        print >>stream, '<!DOCTYPE html>'
        HtmlFragment.print_on(self, stream)

    def to_file(self, file_name):
        import codecs
        f = codecs.open(file_name, 'w', 'UTF-8')
        self.print_on(f)
        f.close()


class HtmlElement(HtmlFragment):
    def __init__(self, document, tag, separate_closing_tag):
        HtmlFragment.__init__(self)
        self._document = document
        self.tag = tag
        self._separate_closing_tag = separate_closing_tag

    def _hookup_to_parent(self, child):
        self.append_child(child)

    def document(self):
        return self._document

    # __enter__ and __exit__ enable use of 'with' statement
    def __enter__(self):
        self.document().stack.append(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.document().stack.pop()

    def attr(self, **kw):
        self.attributes = kw
        return self

    def print_on(self, stream):
        def attribute_key_to_string(k):
            return attribute_names[k] if k in attribute_names else k

        def attribute_to_string(kv):
            return u'%s="%s"' % (attribute_key_to_string(kv[0]),
                                 unicode(kv[1]))

        def attributes_to_string(attrs):
            if len(attrs):
                return u' ' + u' '.join([attribute_to_string(kv)
                                         for kv in attrs.items()])
            else:
                return u''

        attributes_string = attributes_to_string(self.attributes)

        if self._separate_closing_tag:
            tag_open = u'<%s%s>' % (self.tag, attributes_string)
            tag_close = u'</%s>' % self.tag
            if len(self.children):
                print >>stream, tag_open
                HtmlFragment.print_on(self, stream)
                print >>stream, tag_close
            else:
                print >>stream, tag_open + tag_close
        else:
            print >>stream, u'<%s%s/>' % (self.tag, attributes_string)


class HtmlText():
    def __init__(self, txt):
        self.text = txt

    def print_on(self, stream):
        print >>stream, escape(self.text)


class HtmlComment():
    def __init__(self, txt):
        if (txt.find('-->') != -1):
            print >>sys.stderr, 'Unable to deal with \'-->\' in comment string.'
            sys.exit(1)
        self.text = txt

    def print_on(self, stream):
        print >>stream, '<!--', self.text, '-->'


class HtmlSource():
    def __init__(self, txt):
        self.text = txt

    def print_on(self, stream):
        print >>stream, self.text
