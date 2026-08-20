# Spans and Trees

A small Python library for converting between XML trees and a span-based structure. This can be useful for extracting sections of text from XML documents and doing special things with some of the tags.

The two main functions are **tree_to_spans** and **spans_to_tree** for converting between an ElementTree element and text with a list of spans. Examples are shown below.

## tree_to_spans

First create a little example XML tree to convert.

```python
import xml.etree.ElementTree as ET

xmlstring = "<doc><title>Important document</title><contents>Empty</contents></doc>"
root = ET.ElementTree(ET.fromstring(xmlstring)).getroot()
```

Then use the tree_to_spans function to convert the XML document into the text content with spans.

```python
from spans_and_trees import tree_to_spans

text, spans = tree_to_spans(root)

print(text)  # Important documentEmpty
print(spans) # [(0, 18, 'title', {}), (18, 5, 'contents', {})]
```

The format of the spans are a tuple of length 4. The element contents are:

1. The start location of the span
2. The length of the span
3. The tag of the span
4. A dictionary of the attributes of the span.

## spans_to_tree

Now we create a dummy document with a block of text and a span at particular offset.

```python
from spans_and_trees import spans_to_tree

text = 'The quick brown fox jumped over the lazy dog'
spans = [ (10,5,'colour',{'dummy_attrib':'5'}) ] # The span starts at 10, has length of 5, is a 'colour' tag and has a dummy attribute.

root = spans_to_tree(text, spans)

print(type(root)) # <class 'xml.etree.ElementTree.Element'>
```

We can check the XML tree that has been created:

```python
xmlstr = ET.tostring(root)

print(xmlstr) # b'<anon>The quick <colour dummy_attrib="5">brown</colour> fox jumped over the lazy dog</anon>'
```
