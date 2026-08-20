import unicodedata

PMC_IGNORE_TAGS = {
	"table",
	"table-wrap",
	"disp-formula",
	"inline-formula",
	"ref-list",
	"bio",
	"ack",
	"graphic",
	"media",
	"tex-math",
	"mml:math",
	"object-id",
	"ext-link",
}

PMC_SPLIT_TAGS = {
	"table",
	"table-wrap",
	"title",
	"p",
	"sec",
	"break",
	"def-item",
	"list-item",
	"caption",
}

PMC_KEEP_TAGS = {
	"sup",
	"sub",
	"italic",
	"bold",
	"underline",
	"monospace",
	"sc",
	"overline",
	"strike",
}

def cleanup_text(text):
	orig_text = str(text)

	# Remove some "control-like" characters (left/right separator)
	text = text.replace("\u2028", " ").replace("\u2029", " ")
	text = "".join(ch if unicodedata.category(ch)[0] != "C" else " " for ch in text )
	text = "".join(ch if unicodedata.category(ch)[0] != "Z" else " " for ch in text )

	dash_characters = ["-", "\u00ad", "\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2043", "\u2053"]
	for dc in dash_characters:
		text = text.replace(dc,"-")

	assert len(text) == len(orig_text)

	return text

def spans_to_passages(text, spans, ignore_tags=PMC_IGNORE_TAGS, split_tags=PMC_SPLIT_TAGS, keep_tags=PMC_KEEP_TAGS):
	altered_text = cleanup_text(text)
	
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
