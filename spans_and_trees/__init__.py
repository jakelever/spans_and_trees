import xml.etree.cElementTree as etree
from intervaltree import IntervalTree
import unicodedata

def treeToSpans(elem,is_root=True):
	assert isinstance(elem, etree.Element), "treeToSpans expects an ElementTree element"

	# Extract any raw text directly in XML element or just after
	head = ""
	if elem.text:
		head = elem.text
	tail = ""
	if elem.tail and not is_root:
		tail = elem.tail
		
	offset = len(head)
		
	# Then get the text from all child XML nodes recursively
	children_text,children_spans = "",[]
	for child in elem:
		child_text,child_spans = treeToSpans(child,is_root=False)
		children_text += child_text
		
		child_spans = [ (start+offset,length,tag,attrib) for start,length,tag,attrib in child_spans ]
		offset += len(child_text)
		
		children_spans += child_spans

	text = head + children_text + tail
	
	if is_root:
		spans = children_spans
	else:
		span = (0, len(head + children_text), elem.tag, elem.attrib)
		spans = [ span ] + children_spans
		
    # Sort the spans by start, length (reversed) and the tag name
	spans = sorted(spans, key=lambda x:(x[0],-x[1],x[2]))
	
	return text, spans
	
def spansIntersect(a, b):
	a_start,a_end = a[0], a[0]+a[1]
	b_start,b_end = b[0], b[0]+b[1]
	
	assert a_end >= a_start
	assert b_end >= b_start
	
	if a_end <= b_start:
		return False
	elif b_end <= a_start:
		return False
	else:
		return True
	
def spanContainsSpan(parent,child):
	parent_start,parent_end = parent[0], parent[0]+parent[1]
	child_start,child_end = child[0], child[0]+child[1]
	
	contains = (parent_start <= child_start and child_end <= parent_end)
	return contains
	
def spansToTree(text, spans):

	# Do some type checking
	assert isinstance(text, str), "text parameter must be a string"
	assert isinstance(spans, list), "spans parameter must be a list of spans"
	span_format_error = "span must be a tuple with four elements. The first is the offset, the second is the length, the third is the name and the fourth is a dictionary of attributes (with string keys and values)"
	for span in spans:
		assert isinstance(span, tuple), span_format_error
		assert len(span) == 4, span_format_error
		assert isinstance(span[0], int), span_format_error
		assert isinstance(span[1], int), span_format_error
		assert isinstance(span[2], str), span_format_error
		assert isinstance(span[3], dict), span_format_error
	
		for key,value in span[3].items():
			assert isinstance(key,str), span_format_error
			assert isinstance(value,str), span_format_error
	

    # Sort the spans by start, length (reversed) and the tag name
	spans = sorted(spans, key=lambda x:(x[0],-x[1],x[2]))
	
	if len(spans) > 0:
		first_span_start = spans[0][0]
		head = text[:first_span_start]
	else:
		head = text
		
	elem = etree.Element("anon")
	elem.text = head
	
		
		
	while len(spans) > 0:
		current_span = spans[0]
		spans = spans[1:]
		
		is_subspan = [ spanContainsSpan(current_span,s) for s in spans ]
			
		subspans = [ s for s,flag in zip(spans,is_subspan) if flag ]
		spans = [ s for s,flag in zip(spans,is_subspan) if not flag ]
		
		current_span_start = current_span[0]
		current_span_end = current_span[0]+current_span[1]
		if len(spans) > 0:
			next_span_start = spans[0][0]
			tail = text[current_span_end:next_span_start]
		else:
			tail = text[current_span_end:]
		
		subtext = text[current_span_start:current_span_end]
		subspans = [ (start-current_span_start,length,tag,attrib) for start,length,tag,attrib in subspans ]
		
		child_elem = spansToTree(subtext,subspans)
		child_elem.tail = tail
		child_elem.tag = current_span[2]
		child_elem.attrib = current_span[3]
		
		elem.append(child_elem)
		
	return elem
	
def cleanupText(text):
	# Remove some "control-like" characters (left/right separator)
	text = text.replace(u"\u2028", " ").replace(u"\u2029", " ")
	text = "".join(ch if unicodedata.category(ch)[0] != "C" else " " for ch in text )
	text = "".join(ch if unicodedata.category(ch)[0] != "Z" else " " for ch in text )
	
	dash_characters = ["-", "\u00ad", "\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2043", "\u2053"]
	for dc in dash_characters:
		text = text.replace(dc,"-")

	return text
	
def spansToPassages(text, spans):
	tags_to_ignore = { "table", "table-wrap", "disp-formula",
    "inline-formula",
    "ref-list",
    "bio",
    "ack",
    "graphic",
    "media",
    "tex-math",
    "mml:math",
    "object-id",
    "ext-link"}
	
	tags_to_split_at = {"table","table-wrap","title","p","sec","break","def-item","list-item","caption"}
	
	tags_to_annotate = {"Annotation"}
	
	altered_text = cleanupText(text)
	assert len(text) == len(altered_text)
	
	span_tree = IntervalTree()
	
	split_points = [0, len(altered_text)]
	for start,length,tag,attrib in spans:
		end = start+length
		if tag in tags_to_ignore:
			altered_text = altered_text[:start] + ' '*length + altered_text[end:]
		if tag in tags_to_split_at:
			split_points += [start,end]
		if tag in tags_to_annotate:
			span_tree.addi(start,end,(tag,attrib))
			
	split_points = sorted(set(split_points))
	
	passages = []
		
	for i in range(len(split_points)-1):
		start,end = split_points[i],split_points[i+1]
		passage_text = altered_text[start:end]
		
		before_space = len(passage_text) - len(passage_text.lstrip())
		after_space = len(passage_text) - len(passage_text.rstrip())
		
		passage_text = passage_text.strip()
		
		if passage_text:
			start += before_space
			end -= after_space
			
			annotations = []
			for interval in span_tree[start:end]:
				#print(interval.begin, interval.end, interval.data)
				annotation = { 'start':interval.begin, 'end':interval.end, 'tag':interval.data[0], 'attrib':interval.data[1]}
				annotations.append(annotation)
			
			passage = {'start':start,'end':end,'text':passage_text,'annotations':annotations}
			passages.append(passage)
			
	return passages
			
            