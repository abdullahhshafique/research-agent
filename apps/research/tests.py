from django.test import TestCase
from apps.research.services.chunker import TextChunker


class ChunkerTests(TestCase):
    def setUp(self):
        self.chunker = TextChunker(chunk_size=100, overlap=20)
    
    def test_chunk_small_text(self):
        text = "This is a short text."
        chunks = self.chunker.chunk_text(text)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].content, text)
    
    def test_chunk_large_text(self):
        # Create multiple paragraphs to force chunking
        text = ""
        for i in range(10):
            text += f"This is paragraph number {i} with enough text to fill space.\n\n"
        chunks = self.chunker.chunk_text(text)
        self.assertGreater(len(chunks), 1)
    
    def test_chunk_preserves_source_info(self):
        text = "Test content"
        chunks = self.chunker.chunk_text(text, source_url="http://example.com", source_title="Example")
        self.assertEqual(chunks[0].source_url, "http://example.com")
        self.assertEqual(chunks[0].source_title, "Example")
    
    def test_chunk_sources_empty(self):
        chunks = self.chunker.chunk_sources([])
        self.assertEqual(len(chunks), 0)
    
    def test_chunk_sources_multiple(self):
        sources = [
            {'content': 'Source one content', 'url': 'http://one.com', 'title': 'One'},
            {'content': 'Source two content', 'url': 'http://two.com', 'title': 'Two'},
        ]
        chunks = self.chunker.chunk_sources(sources)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].index, 0)
        self.assertEqual(chunks[1].index, 1)