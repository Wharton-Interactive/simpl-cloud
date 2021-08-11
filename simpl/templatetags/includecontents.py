from collections import abc

from django import template
from django.template import TemplateSyntaxError
from django.template.base import TokenType
from django.template.loader_tags import do_include
from django.utils.safestring import mark_safe

register = template.Library()


@register.tag
def includecontents(parser, token):
    """
    An extension of the ``{% include %}`` tag which loads a template and
    renders it with the current context. It accepts all the standard
    include tag arguments.

    The contents of this block tag is made available as a ``contents``
    variable in the context of the included template.

    Use ``{% contents some_name %}`` to use named areas which are
    available as ``contents.some_name`` in the context of the included
    template.

    Example::

        {% includecontents "includes/dialog.html" with dismissable=False %}
        Default contents lives outside a named area.
        {% contents title %}
            The contents of the named area called &quot;title&quot;.
        {% endcontents %}
        Default contents can live both before and after named areas at the same time.
        {% endincludecontents %}

    Included Template:

        <div class="dialog"{% if dismissable %} data-dismissable{% endif %}>
            {% if contents.title %}
                <h3>{{ contents.title }}</h3>
            {% endif %}
            <section>
            {{ contents }}
            </section>
            <button>{{ contents.save|default:"Save" %}</button>
            {% if "note" in contents %}
                {% if contents.note %}
                    <small>{{ contents.note }}</small>
                {% endif %}
            {% else %}
                <small>Default note only shown if named area wasn't provided.</small>
            {% endif %}
        </div>
    """
    nodelist, named_nodelists = get_contents_nodelists(parser)
    include_node = do_include(parser, token)
    include_node.origin = parser.origin
    return IncludeContentsNode(
        include_node=include_node,
        nodelist=nodelist,
        named_nodelists=named_nodelists,
    )


class RenderedContents(abc.Mapping):
    def __init__(self, context, nodelist, named_nodelists=None):
        with context.push():
            self.rendered_contents = mark_safe(nodelist.render(context).strip())
        self.rendered_areas = {}
        for key, named_nodelist in named_nodelists.items():
            with context.push():
                rendered_area = named_nodelist.render(context)
                if not rendered_area.strip():
                    rendered_area = ""
            self.rendered_areas[key] = mark_safe(rendered_area)

    def __str__(self):
        return self.rendered_contents

    def __getitem__(self, key):
        return self.rendered_areas[key]

    def __iter__(self):
        return iter(self.rendered_areas)

    def __len__(self):
        return len(self.rendered_contents)


class IncludeContentsNode(template.Node):
    def __init__(self, include_node, nodelist, named_nodelists):
        self.include_node = include_node
        self.nodelist = nodelist
        self.named_nodelists = named_nodelists

    def render(self, context):
        with context.push():
            context["contents"] = RenderedContents(
                context, nodelist=self.nodelist, named_nodelists=self.named_nodelists
            )
            return self.include_node.render(context)


def get_contents_nodelists(parser):
    end_tag = "endincludecontents"
    named_nodelists = {}
    default = []

    depth = 0
    while parser.tokens:
        token = parser.next_token()
        if token.token_type != TokenType.BLOCK:
            default.append(token)
            continue
        bits = token.split_contents()
        tag_name = bits[0]

        if tag_name == "includecontents":
            depth += 1
        elif tag_name == "contents" and not depth:
            if len(bits) < 2:
                raise TemplateSyntaxError(
                    "Unnamed %r tag within includecontents" % tag_name
                )
            if len(bits) > 2:
                raise TemplateSyntaxError("Invalid %r tag format" % tag_name)
            area_name = bits[1]
            if area_name in named_nodelists:
                raise TemplateSyntaxError(
                    "Duplicate name for %r tag: %r" % (tag_name, area_name)
                )
            named_nodelists[area_name] = parser.parse(["end" + tag_name])
            parser.delete_first_token()
            continue
        elif tag_name == end_tag:
            if depth:
                depth -= 1
            else:
                default.append(token)
                for default_token in reversed(default):
                    parser.prepend_token(default_token)
                nodelist = parser.parse([end_tag])
                parser.delete_first_token()
                return nodelist, named_nodelists
        default.append(token)
    parser.unclosed_block_tag([end_tag])
