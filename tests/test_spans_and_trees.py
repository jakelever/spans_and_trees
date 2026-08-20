import xml.etree.ElementTree as ET

import pytest

from spans_and_trees import (
	cleanupText,
	spanContainsSpan,
	spans_to_tree,
	spansIntersect,
	spansToPassages,
	tree_to_spans,
)


def parse(xmlstring):
	return ET.ElementTree(ET.fromstring(xmlstring)).getroot()


class TestTreeToSpans:
	def test_simple_siblings(self):
		root = parse("<doc><title>Important document</title><contents>Empty</contents></doc>")
		text, spans = tree_to_spans(root)

		assert text == "Important documentEmpty"
		assert spans == [(0, 18, "title", {}), (18, 5, "contents", {})]

	def test_nested_elements(self):
		root = parse("<doc>A<b>B<c>C</c></b>D</doc>")
		text, spans = tree_to_spans(root)

		assert text == "ABCD"
		assert spans == [(1, 2, "b", {}), (2, 1, "c", {})]

	def test_attributes_are_preserved(self):
		root = parse('<doc><span colour="red">hi</span></doc>')
		text, spans = tree_to_spans(root)

		assert text == "hi"
		assert spans == [(0, 2, "span", {"colour": "red"})]

	def test_root_tag_itself_is_not_a_span(self):
		root = parse("<doc>hello</doc>")
		text, spans = tree_to_spans(root)

		assert text == "hello"
		assert spans == []

	def test_rejects_non_element_input(self):
		with pytest.raises(AssertionError):
			tree_to_spans("not an element")


class TestSpansToTree:
	def test_simple_span(self):
		text = "The quick brown fox jumped over the lazy dog"
		spans = [(10, 5, "colour", {"dummy_attrib": "5"})]

		root = spans_to_tree(text, spans)

		assert root.text == "The quick "
		child = list(root)[0]
		assert child.tag == "colour"
		assert child.text == "brown"
		assert child.attrib == {"dummy_attrib": "5"}
		assert child.tail == " fox jumped over the lazy dog"

	def test_nested_spans(self):
		text = "ABCD"
		spans = [(1, 2, "b", {}), (2, 1, "c", {})]

		root = spans_to_tree(text, spans)

		b = list(root)[0]
		assert b.tag == "b"
		assert b.text == "B"
		assert b.tail == "D"

		c = list(b)[0]
		assert c.tag == "c"
		assert c.text == "C"

	def test_no_spans_returns_plain_text(self):
		root = spans_to_tree("hello", [])
		assert root.text == "hello"
		assert list(root) == []

	def test_rejects_non_string_text(self):
		with pytest.raises(AssertionError):
			spans_to_tree(123, [])

	def test_rejects_non_list_spans(self):
		with pytest.raises(AssertionError):
			spans_to_tree("hello", "not a list")

	@pytest.mark.parametrize("bad_span", [
		(0, 1, "tag"),  # wrong length
		("0", 1, "tag", {}),  # start not int
		(0, "1", "tag", {}),  # length not int
		(0, 1, 5, {}),  # tag not str
		(0, 1, "tag", []),  # attrib not dict
		(0, 1, "tag", {1: "a"}),  # attrib key not str
		(0, 1, "tag", {"a": 1}),  # attrib value not str
	])
	def test_rejects_malformed_spans(self, bad_span):
		with pytest.raises(AssertionError):
			spans_to_tree("hello", [bad_span])


class TestRoundTrip:
	@pytest.mark.parametrize("xmlstring", [
		"<doc><title>Important document</title><contents>Empty</contents></doc>",
		"<doc>A<b>B<c>C</c></b>D</doc>",
		'<doc><span colour="red">hi</span></doc>',
		"<doc>just text, no children</doc>",
	])
	def test_tree_spans_tree_round_trip(self, xmlstring):
		original_root = parse(xmlstring)
		text, spans = tree_to_spans(original_root)

		rebuilt_root = spans_to_tree(text, spans)
		rebuilt_text, rebuilt_spans = tree_to_spans(rebuilt_root)

		assert rebuilt_text == text
		assert rebuilt_spans == spans


class TestSpansIntersect:
	def test_overlapping(self):
		assert spansIntersect((0, 5, "a", {}), (3, 5, "b", {})) is True

	def test_touching_but_not_overlapping(self):
		assert spansIntersect((0, 5, "a", {}), (5, 5, "b", {})) is False

	def test_disjoint(self):
		assert spansIntersect((0, 2, "a", {}), (10, 2, "b", {})) is False


class TestSpanContainsSpan:
	def test_contains(self):
		assert spanContainsSpan((0, 10, "a", {}), (2, 3, "b", {})) is True

	def test_does_not_contain(self):
		assert spanContainsSpan((0, 5, "a", {}), (3, 5, "b", {})) is False

	def test_exact_match_counts_as_containing(self):
		assert spanContainsSpan((0, 5, "a", {}), (0, 5, "b", {})) is True


class TestCleanupText:
	def test_replaces_control_and_separator_characters_with_space(self):
		text = "hello world !"
		assert cleanupText(text) == "hello world !"

	def test_normalises_dash_characters(self):
		text = "a‐b–c—d"
		assert cleanupText(text) == "a-b-c-d"

	def test_length_is_preserved(self):
		text = "hello world"
		assert len(cleanupText(text)) == len(text)


class TestSpansToPassages:
	def test_splits_on_paragraph_tags(self):
		first, second = "First paragraph.", "Second paragraph."
		text = first + second
		spans = [
			(0, len(first), "p", {}),
			(len(first), len(second), "p", {}),
		]

		passages = spansToPassages(text, spans)

		assert [p["text"] for p in passages] == [first, second]

	def test_annotations_are_attached_to_passages(self):
		before, word, after = "Some ", "annotated", " text here."
		text = before + word + after
		start, end = len(before), len(before) + len(word)
		spans = [
			(0, len(text), "p", {}),
			(start, len(word), "Annotation", {"type": "example"}),
		]

		passages = spansToPassages(text, spans)

		assert len(passages) == 1
		assert passages[0]["annotations"] == [
			{"start": start, "end": end, "tag": "Annotation", "attrib": {"type": "example"}}
		]

	def test_ignored_tags_are_blanked_out(self):
		before, ignored, after = "before ", "TABLE_CONTENT", " after"
		text = before + ignored + after
		spans = [(len(before), len(ignored), "table", {})]

		passages = spansToPassages(text, spans)

		assert [p["text"] for p in passages] == ["before", "after"]
