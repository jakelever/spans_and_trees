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

def cleanup_pmc_text(text):
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
