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

### Example: a real PMC article via Entrez

Here the `spans_and_trees.pmc` tag sets are applied to a real open-access article fetched from NCBI's Entrez E-utilities. For PMC articles, there is a helper function `cleanup_pmc_text` which does some cleaning of common Unicode problems. There are also pre-prepared tag lists for PMC to ignore, split on and keep.

```python
from spans_and_trees.pmc import cleanup_pmc_text, PMC_IGNORE_TAGS, PMC_SPLIT_TAGS, PMC_KEEP_TAGS

import urllib.request

pmcid = "7096066"  # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7096066/
url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid}&rettype=full&retmode=xml"

with urllib.request.urlopen(url) as response:
	root = ET.fromstring(response.read())

body = root.find(".//body")
text, spans = tree_to_spans(body)
text = cleanup_pmc_text(text)
passages = spans_to_passages(text, spans, ignore_tags=PMC_IGNORE_TAGS, split_tags=PMC_SPLIT_TAGS, keep_tags=PMC_KEEP_TAGS)

print(passages[0])
# {'start': 0, 'end': 27, 'text': 'Introduction and background', 'spans': []}
```
