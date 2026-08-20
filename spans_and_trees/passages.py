from .core import validate_spans
from .pmc import cleanup_pmc_text


def spans_to_passages(text, spans, ignore_tags, split_tags, keep_tags):
	assert isinstance(text, str), "text parameter must be a string"
	validate_spans(spans)

	altered_text = cleanup_pmc_text(text)
	
	split_points = [0, len(altered_text)]
	for start,length,tag,attrib in spans:
		end = start+length
		if tag in ignore_tags:
			altered_text = altered_text[:start] + ' '*length + altered_text[end:]
		if tag in split_tags:
			split_points += [start,end]

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

			selected_spans = [ (s,length,tag,attrib) for s,length,tag,attrib in spans if s < end and s+length > start and tag in keep_tags ]
			truncated_spans = [ (max(s,start)-start,min(s+length,end)-max(s,start),tag,attrib) for s,length,tag,attrib in selected_spans ]

			passage = {'start':start,'end':end,'text':passage_text,'spans':truncated_spans}
			passages.append(passage)

	return passages
