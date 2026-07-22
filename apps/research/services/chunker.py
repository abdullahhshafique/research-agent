"""
Text chunking service for processing large documents.
Splits text into manageable chunks while preserving context.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class TextChunk:
    """Represents a chunk of text with metadata."""
    
    def __init__(self, content: str, index: int, source_url: str = "", source_title: str = ""):
        self.content = content
        self.index = index
        self.source_url = source_url
        self.source_title = source_title
        self.word_count = len(content.split())
    
    def __repr__(self) -> str:
        return f"TextChunk(index={self.index}, words={self.word_count})"


class TextChunker:
    """
    Intelligent text chunking for LLM processing.
    
    Splits text into chunks that fit within token limits while preserving
    paragraph boundaries and context.
    """
    
    # Character limits (roughly 1 token ≈ 4 chars for English)
    DEFAULT_MAX_CHARS = 60000  # ~15K tokens
    CHUNK_SIZE = 12000         # ~3K tokens per chunk
    OVERLAP = 2000             # ~500 tokens overlap
    
    def __init__(self, max_chars: int = DEFAULT_MAX_CHARS, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP):
        self.max_chars = max_chars
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, source_url: str = "", source_title: str = "", chunk_size: int = None, overlap: int = None) -> List[TextChunk]:
        """
        Split text into chunks.
        
        Args:
            text: Input text to chunk
            source_url: Source URL for attribution
            source_title: Source title for attribution
            chunk_size: Override default chunk size (optional)
            overlap: Override default overlap (optional)
            
        Returns:
            List of TextChunk objects
        """
        # Use provided values or fall back to instance defaults
        effective_chunk_size = chunk_size if chunk_size is not None else self.chunk_size
        effective_overlap = overlap if overlap is not None else self.overlap
        
        if not text or len(text.strip()) == 0:
            return []
        
        # If text is small enough, return as single chunk
        if len(text) <= effective_chunk_size:
            return [TextChunk(text, 0, source_url, source_title)]
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_index = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            paragraph_length = len(paragraph)
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if current_length + paragraph_length > effective_chunk_size and current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append(TextChunk(chunk_text, chunk_index, source_url, source_title))
                
                # Start new chunk with overlap
                overlap_text = chunk_text[-effective_overlap:] if len(chunk_text) > effective_overlap else chunk_text
                current_chunk = [overlap_text, paragraph]
                current_length = len(overlap_text) + paragraph_length
                chunk_index += 1
            else:
                current_chunk.append(paragraph)
                current_length += paragraph_length
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(TextChunk(chunk_text, chunk_index, source_url, source_title))
        
        logger.info(f"Chunked text into {len(chunks)} chunks (total chars: {len(text)})")
        return chunks
    
    def chunk_sources(self, sources: List[Dict[str, Any]]) -> List[TextChunk]:
        """
        Chunk multiple sources into a single list.
        
        Args:
            sources: List of source dicts with 'content', 'url', 'title' keys
            
        Returns:
            Combined list of TextChunk objects
        """
        all_chunks = []
        chunk_index = 0
        
        for source in sources:
            content = source.get('content', '')
            url = source.get('url', '')
            title = source.get('title', 'Untitled')
            
            if not content:
                continue
            
            # Chunk this source
            source_chunks = self.chunk_text(content, url, title)
            
            # Re-index globally
            for chunk in source_chunks:
                chunk.index = chunk_index
                all_chunks.append(chunk)
                chunk_index += 1
        
        logger.info(f"Total chunks from {len(sources)} sources: {len(all_chunks)}")
        return all_chunks