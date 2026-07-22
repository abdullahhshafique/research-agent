"""
Report builder service -- assembles Markdown reports from research data.
"""
from apps.research.models import ResearchQuery


class ReportBuilder:
    """
    Builds structured Markdown reports from research queries.
    """
    
    def __init__(self, title: str = "", query: str = ""):
        self.title = title
        self.query = query
        self.summary = ""
        self.insight = ""
        self.sources = []
        self.metadata = {}
    
    def add_summary(self, summary: str):
        """Add the main summary section."""
        self.summary = summary
        return self
    
    def add_sources(self, sources: list):
        """Add source references."""
        self.sources = sources
        return self
    
    def add_insight(self, insight: str):
        """Add final insight/conclusion."""
        self.insight = insight
        return self
    
    def add_metadata(self, metadata: dict):
        """Add report metadata."""
        self.metadata = metadata
        return self
    
    def build(self) -> str:
        """Build the complete Markdown report."""
        lines = []
        
        # Title
        lines.append(f"# {self.title}")
        lines.append("")
        lines.append(f"**Query:** {self.query}")
        lines.append("")
        
        # Metadata
        if self.metadata:
            lines.append("---")
            lines.append("")
            for key, value in self.metadata.items():
                lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Summary
        if self.summary:
            lines.append("## Summary")
            lines.append("")
            lines.append(self.summary)
            lines.append("")
        
        # Sources
        if self.sources:
            lines.append("## Sources")
            lines.append("")
            for i, source in enumerate(self.sources, 1):
                title = source.get('title', 'Untitled')
                url = source.get('url', '#')
                domain = source.get('domain', '')
                score = source.get('score', 0)
                lines.append(f"{i}. [{title}]({url}) -- {domain} (relevance: {score:.2f})")
            lines.append("")
        
        # Insight
        if self.insight:
            lines.append("## Final Insight")
            lines.append("")
            lines.append(self.insight)
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def from_research_query(cls, research: ResearchQuery) -> str:
        """Build report from an existing ResearchQuery instance."""
        builder = cls(
            title=f"Research Report: {research.query_text[:50]}",
            query=research.query_text
        )
        
        if research.summary:
            builder.add_summary(research.summary)
        
        if research.final_insight:
            builder.add_insight(research.final_insight)
        
        # Get sources from DB
        sources = []
        for source in research.sources.all():
            sources.append({
                'url': source.url,
                'title': source.title or 'Untitled',
                'domain': source.domain,
                'score': source.relevance_score or 0,
            })
        builder.add_sources(sources)
        
        # Metadata
        builder.add_metadata({
            'source_count': len(sources),
            'search_depth': research.search_depth,
            'llm_model': research.llm_model,
            'generated_at': research.completed_at.isoformat() if research.completed_at else 'N/A',
        })
        
        return builder.build()