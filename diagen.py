#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2018 Hornwitser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from xml.etree.ElementTree import Comment, Element, ElementTree, SubElement
from collections import namedtuple
from itertools import count

__all__ = [
    'Label', 'Choice', 'Condition', 'AnyCondition', 'Goto', 'End',
    'Event', 'Response', 'xml_dialogues', 'xml_pretty',
]


# Message Dirictives

# Set the next message's id
Label = namedtuple('Label', 'id')

# Signal the end of the message stream.
class EndType:
    def __new__(cls):
        return End

    @staticmethod
    def __repr__():
        return 'End'

End = object.__new__(EndType)

# Continue with given id.
Goto = namedtuple('Goto', 'target')

# Attach an event to the previous message.
Event = namedtuple('Event', 'id target')

# Set the reply text of the previous message.
Response = namedtuple('Response', 'text')

# Specifies a multiple choice message.  Choices is a list of subsections.  The
# reply element generated can be modified with Response, Condition,
# AnyCondition, Goto and End put at the start of a choice subsection
Choice = namedtuple('Choice', 'text choices')

# Specifies the condition of a choice.  May only be used at the start of a
# choice subsection.
_BaseCondition = namedtuple('Condition', 'type params')
class Condition(_BaseCondition):
    def __new__(cls, type, params={}, **extra):
        return super().__new__(cls, type, {**params, **extra})


# Specifies the any_condition attribute of a reply.  May only be used at the
# start of a choice subsection.
AnyCondition = namedtuple('AnyCondition', 'value')


# Internal use types
class AutoType:
    def __new__(cls):
        return Auto

    @staticmethod
    def __repr__():
        return 'Auto'

Auto = object.__new__(AutoType)

class ParsedReply:
    def __init__(self, target, text):
        self.id = Auto
        self.target = target
        self.text = text
        self.conditions = []
        self.any_condition = None

class ParsedMessage:
    def __init__(self, mid, text):
        self.id = mid
        self.text = text
        self.next = Auto
        self.response = Auto
        self.choices = []
        self.events = []

FlatMessage = namedtuple('FlatMessage', 'id text replies events')
FlatReply = namedtuple('FlatReply', 'id target text conditions any_condition')

def auto(value, auto_value):
    """Replace a value being Auto with auto_value"""
    return auto_value if value is Auto else value

def parse_reply(pos, section):
    """Parse reply modifiers from the start of a subsection"""
    reply = ParsedReply(Auto, Auto)
    while pos < len(section):
        mod = section[pos]

        if type(mod) is Response:
            reply.text = mod.text

        elif type(mod) is Condition:
            reply.conditions.append(mod)

        elif type(mod) is AnyCondition:
            reply.any_condition = mod.value

        elif mod is End:
            reply.target = None

        elif type(mod) is Goto:
            reply.target = mod.target

        else:
            break
        pos += 1
    return pos, reply

def parse_message(pos, section):
    """Parse message with associated modifiers"""
    mid = Auto

    if type(section[pos]) is Label:
        if pos == len(section):
            raise TypeError("Label is not allowed at the end of a section")

        mid = section[pos].id
        pos += 1

    if type(section[pos]) is str:
        message = ParsedMessage(mid, section[pos])
        pos += 1

    elif type(section[pos]) is Choice:
        choices = []
        for content in section[pos].choices:
            subpos, reply = parse_reply(0, content)
            _, subsection = parse_dialogue(subpos, content)
            choices.append((reply, subsection))

        message = ParsedMessage(mid, section[pos].text)
        message.choices.extend(choices)
        pos += 1

    elif mid is not Auto:
        msg = f"{section[pos].__class__.__name__} is not allowed after a Label"
        raise TypeError(msg)

    else:
        raise TypeError(f"parse_message called on {section[pos]}")

    while pos < len(section):
        item = section[pos]

        if item is End:
            message.next = None

        elif type(item) is Goto:
            message.next = item.target

        elif type(item) is Event:
            message.events.append(item)

        elif type(item) is Response:
            message.response = item.text

        else:
            break
        pos += 1
    return pos, message


def parse_dialogue(pos, section):
    """Parse message objects and modifiers"""
    if type(section) is tuple and len(section) == 1:
        msg = f"Got section packed into one element tuple, content: {section}"
        raise TypeError(msg)

    dialogue = []
    while pos < len(section):
        item = section[pos]

        if type(item) in [Label, Choice, str]:
            pos, message = parse_message(pos, section)
            dialogue.append(message)
            continue

        elif type(item) in [
            Condition, AnyCondition, EndType, Goto, Event, Response
        ]:
            msg = f"{item.__class__.__name__} is not allowed here"
            raise TypeError(msg)

        else:
            msg = f"Unkown item type {item.__class__.__name__}, value: {item}"
            raise TypeError(msg)

        pos += 1

    return pos, dialogue

def assign_ids(section, mid_gen):
    """Assign ids for messages and replies that has Auto as the id"""

    for item in section:
        if item.id is Auto:
            item.id = next(mid_gen)

        # If there are more than 9 choices, R10 will sort before R2
        if len(item.choices) > 9:
            rid_gen = map("R{:02}".format, count(1))
        else:
            rid_gen = map("R{}".format, count(1))

        for reply, sub in item.choices:
            if reply.id is Auto:
                reply.id = next(rid_gen)

            assign_ids(sub, mid_gen)

def resolve(section, end=None):
    """Resolve next, target and reply text references that are set to Auto"""
    for i, item in enumerate(section):
        if item.next is Auto:
            item.next = section[i+1].id if i+1 < len(section) else end

        for reply, sub in item.choices:
            if reply.target is Auto:
                reply.target = sub[0].id if sub else item.next

            if reply.text is Auto:
                reply.text = item.response

            resolve(sub, end=item.next)

def flatten(section):
    """Creates a flat representation of a processed section"""
    output = []
    for item in section:
        assert type(item) is ParsedMessage, "Should not be possible"

        replies = []
        sub_outputs = []
        if item.choices:
            for reply, sub in item.choices:
                replies.append(FlatReply(
                    reply.id, reply.target, reply.text,
                    reply.conditions, reply.any_condition
                ))
                sub_outputs.extend(flatten(sub))

        elif item.response is not Auto or item.next is not None:
            replies.append(FlatReply('R1', item.next, item.response, [], None))

        output.append(FlatMessage(item.id, item.text, replies, item.events))
        output.extend(sub_outputs)

    return output

SERVER_VAR_TYPES = [
    "SERVER_VARIABLE_PRESENT",
    "SERVER_VARIABLE_ABSENT",
]

def xml_params(node, param_node_name, params):
    """Add possibly duplicated params to node"""
    for key, value in params.items():
        if type(value) is list:
            for item in value:
                if type(item) is int:
                    item = str(item)
                SubElement(node, param_node_name, {key: item})
        else:
            if type(value) is int:
                value = str(value)
            node.set(key, value)

def xml_conditions(node, node_name, conditions, options):
    """Add xml condition and condition_param nodes from condition list"""
    for condition in conditions:
        if condition.type in SERVER_VAR_TYPES:
            if (
                options['mangle_any_value']
                and 'any_value' in condition.params
                and 'var_value' not in condition.params
            ):
                condition.params['var_value'] = '1'

            if (
                options['mangle_empty_value']
                and 'any_value' not in condition.params
                and 'var_value' not in condition.params
            ):
                index = 1 - SERVER_VAR_TYPES.index(condition.type)
                condition = condition._replace(type=SERVER_VAR_TYPES[index])

        condition_node = SubElement(node, node_name, type=condition.type)
        xml_params(condition_node, 'condition_param', condition.params)

def xml_messages(node, messages, options):
    """Add xml message nodes to dialog node from flat message list"""
    for msg in messages:
        msg_node = SubElement(node, 'message', id=msg.id, text=msg.text)

        for event in msg.events:
            SubElement(msg_node, 'event', id=event.id, target=event.target)

        for reply in msg.replies:
            text = auto(reply.text, options['default_response'])
            reply_node = SubElement(msg_node, 'reply', id=reply.id, text=text)

            if reply.target is not None:
                reply_node.set('next', reply.target)

            if reply.any_condition is not None:
                reply_node.set('any_condition', reply.any_condition)

            xml_conditions(reply_node, 'condition', reply.conditions, options)

def xml_dialogues(dialogues, options):
    """Create dialogues node from diagen dialogue mapping"""
    mid_gen = map("M{}".format, count())

    dialogues_node = Element('dialogues')
    for name, section in dialogues.items():
        _, section = parse_dialogue(0, section)
        assign_ids(section, mid_gen)
        resolve(section)
        messages = flatten(section)
        if not messages:
            raise ValueError(f"'{name}' has no messages")

        dialogue_node = SubElement(dialogues_node, 'dialogue', name=name)

        start_node = SubElement(dialogue_node, 'start')
        start_node.text = messages[0].id

        xml_messages(dialogue_node, messages, options)

    return dialogues_node

def debug_format(item, indent=0):
    """Format a pretty representation of a processed section"""
    if type(item) is ParsedMessage:
        return "\n".join([
            f"{' '*indent}<ParsedMessage id={item.id!r} text={item.text!r}"
            f" next={item.next!r} response={item.response!r}"
            f" events={item.events} choices=["
        ] + [debug_format(c, indent+4) + ',' for c in item.choices] + [
            f"{' '*indent}]>"
        ])

    if type(item) is ParsedReply:
        return (
            f"{' '*indent}<ParsedReply id={item.id!r} target={item.target!r}"
            f" text={item.text!r} conditions={item.conditions}"
            f" any_condition={item.any_condition}>"
        )

    if type(item) is list:
        return "\n".join([
            f"{' '*indent}[",
        ] + [debug_format(sub, indent+4) + ',' for sub in item] + [
            f"{' '*indent}]"
        ])

    if type(item) is tuple:
        return "\n".join([
            f"{' '*indent}(",
        ] + [debug_format(sub, indent+4) + ',' for sub in item] + [
            f"{' '*indent})"
        ])

    return ' ' * indent + repr(item)

def xml_pretty(node, indent=0):
    """Indents and spreads out compact nodes representaions over lines"""
    if len(node):
        text = node.text if node.text is not None else ""
        node.text = f"\n{'    ' * (indent + 1)}{text}"

    for i, sub in enumerate(node):
        tail = sub.tail if sub.tail is not None else ""
        sub.tail = f"\n{'    ' * (indent + (i < len(node)-1))}{tail}"

        xml_pretty(sub, indent+1)

def main():
    """Parse command line argements and do dialogue generation"""
    from argparse import ArgumentParser
    from pathlib import Path
    import sys

    def error(message, code=1):
        """Print message to stderr and exit with code"""
        print(message, file=sys.stderr)
        exit(code)

    def handle_open(path, out):
        """Opens path as output if out otherwise as input"""
        if path == "-":
            return sys.stdout if out else sys.stdin
        try:
            return open(path, 'x' if out else 'r')
        except OSError as err:
            error(f"Error opening {path}: {err}")

    options = {
        'default_response': "[SKIP]...",
        'mangle_any_value': True,
        'mangle_empty_value': True,
    }


    parser = ArgumentParser(description="Generate Tachyion dialogue XML")
    parser.add_argument(
        'script', help="Script file containing the dialogues definition"
    )
    parser.add_argument(
        'output', nargs='?', default=None,
        help="Output file, defaults to script name with an xml extension"
    )

    args = parser.parse_args()

    if args.output is None:
        args.output = Path(args.script).with_suffix('.xml')


    in_file = handle_open(args.script, False)
    out_file = handle_open(args.output, True)

    script_vars = {k: v for k, v in globals().items() if k in __all__}
    exec(in_file.read(), script_vars)

    if 'dialogues' not in script_vars:
        error(f"Script does not set the dialogues variable", 2)

    dialogues = script_vars['dialogues']
    options.update(script_vars.get('diagen_options', {}))
    root = xml_dialogues(dialogues, options)

    root.insert(0, Comment(" Generated by diagen.py "))
    xml_pretty(root)
    root.tail = "\n"

    document = ElementTree(root)
    document.write(out_file, encoding="unicode", xml_declaration=True)

if __name__ == '__main__':
    main()
