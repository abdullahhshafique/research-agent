from django.test import TestCase
from apps.reports.services.report_builder import ReportBuilder


class ReportBuilderTests(TestCase):
    def test_build_basic_report(self):
        builder = ReportBuilder(title="Test Report", query="Test query")
        builder.add_summary("This is a summary.")
        builder.add_sources([
            {'url': 'http://example.com', 'title': 'Example', 'domain': 'example.com', 'score': 0.9}
        ])
        report = builder.build()
        
        self.assertIn("# Test Report", report)
        self.assertIn("Test query", report)
        self.assertIn("This is a summary.", report)
        self.assertIn("Example", report)
    
    def test_build_with_insight(self):
        builder = ReportBuilder(title="Test", query="Query")
        builder.add_insight("Future looks bright.")
        report = builder.build()
        
        self.assertIn("## Final Insight", report)
        self.assertIn("Future looks bright.", report)
    
    def test_build_with_metadata(self):
        builder = ReportBuilder(title="Test", query="Query")
        builder.add_metadata({
            'source_count': 5,
            'processing_time': 45.2,
            'search_depth': 'advanced',
            'llm_model': 'groq'
        })
        report = builder.build()
        
        self.assertIn("5", report)
        self.assertIn("advanced", report)
