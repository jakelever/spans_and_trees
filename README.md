# Spans and Trees

![PyPi](https://img.shields.io/pypi/v/spans_and_trees.svg) ![License](https://img.shields.io/pypi/l/spans_and_trees.svg) [![Tests](https://github.com/jakelever/spans_and_trees/actions/workflows/tests.yml/badge.svg)](https://github.com/jakelever/spans_and_trees/actions) [![codecov](https://codecov.io/gh/jakelever/spans_and_trees/branch/main/graph/badge.svg)](https://codecov.io/gh/jakelever/spans_and_trees)

A small Python library for converting between XML trees and a span-based structure. This can be useful for extracting sections of text from XML documents and doing special things with some of the tags.

The three functions are **tree_to_spans**, **spans_to_tree** and **spans_to_passages** for converting between an ElementTree element and text with a list of spans. Examples are shown below.

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

print(xmlstr) # b'<tree>The quick <colour dummy_attrib="5">brown</colour> fox jumped over the lazy dog</tree>'
```

The root element's tag defaults to `"tree"`, since spans don't record a tag for the whole document (`tree_to_spans` doesn't include one either). Pass `root_tag` to use something else, e.g. `spans_to_tree(text, spans, root_tag="doc")`.

## spans_to_passages

`spans_to_passages` takes the `text`/`spans` output of `tree_to_spans` and splits it into a list of text passages, one per `split_tags` element (e.g. `p`, `sec`), dropping the content of any `ignore_tags` element (e.g. `table`), and attaching any `keep_tags` spans (e.g. `bold`) that fall within each passage.

```python
from spans_and_trees import tree_to_spans, spans_to_passages

xmlstring = """
<article>
	<sec>
		<title>Introduction</title>
		<p>This is <bold>important</bold> background text.</p>
		<table-wrap>Some table content we want to ignore.</table-wrap>
		<p>A second paragraph follows.</p>
	</sec>
</article>
"""

root = ET.ElementTree(ET.fromstring(xmlstring)).getroot()
text, spans = tree_to_spans(root)

passages = spans_to_passages(text, spans, ignore_tags={'table-wrap'}, split_tags={'title','p'}, keep_tags={'bold'})
for p in passages:
	print(p)

# {'start': 5, 'end': 17, 'text': 'Introduction', 'spans': []}
# {'start': 20, 'end': 54, 'text': 'This is important background text.', 'spans': [(8, 9, 'bold', {})]}
# {'start': 97, 'end': 124, 'text': 'A second paragraph follows.', 'spans': []}
```

Each passage's `start`/`end` are offsets into the original `text`; each attached span's offsets are relative to the passage's own `text`.
