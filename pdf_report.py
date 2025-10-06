"""
PDF Report Generator for LMS Activity Monitor
Generates beautiful PDF reports with new activities and upcoming deadlines.
"""

import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class PDFReportGenerator:
    """Generate PDF reports for LMS activities and deadlines."""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize PDF report generator.
        
        Args:
            output_dir: Directory to save generated PDF reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Normal text with better spacing
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14
        ))
    
    def _get_colombo_time(self) -> datetime:
        """Get current time in Colombo timezone (UTC+5:30)."""
        colombo_tz = timezone(timedelta(hours=5, minutes=30))
        return datetime.now(colombo_tz)
    
    def _format_datetime(self, dt_str: str) -> str:
        """Format datetime string to readable format."""
        try:
            if isinstance(dt_str, str):
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            else:
                dt = dt_str
            
            # Convert to Colombo time
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            colombo_tz = timezone(timedelta(hours=5, minutes=30))
            local_dt = dt.astimezone(colombo_tz)
            
            return local_dt.strftime('%b %d, %Y %I:%M %p')
        except:
            return str(dt_str)
    
    def _create_header(self, story: list):
        """Create report header with title and date."""
        current_time = self._get_colombo_time()
        
        # Title
        title = Paragraph("LMS Activity Report", self.styles['CustomTitle'])
        story.append(title)
        
        # Date
        date_text = current_time.strftime('%A, %B %d, %Y')
        date_para = Paragraph(f"<i>{date_text}</i>", self.styles['CustomBody'])
        story.append(date_para)
        story.append(Spacer(1, 0.3 * inch))
    
    def _create_summary_section(self, story: list, stats: Dict):
        """Create summary statistics section."""
        summary = Paragraph("Summary", self.styles['CustomSubtitle'])
        story.append(summary)
        
        # Summary table
        summary_data = [
            ['Total Courses', str(stats.get('total_courses', 0))],
            ['Total Activities', str(stats.get('total_activities', 0))],
            ['New Activities', str(stats.get('new_activities', 0))],
            ['Last Scan', self._format_datetime(stats.get('last_scan_time', 'Never'))]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))
    
    def _create_activities_section(self, story: list, activities: List[Dict]):
        """Create new activities section."""
        if not activities:
            return
        
        header = Paragraph(f"New Activities ({len(activities)})", self.styles['CustomSubtitle'])
        story.append(header)
        
        # Group by LMS
        ousl_activities = [a for a in activities if a.get('lms_name') == 'OUSL']
        rusl_activities = [a for a in activities if a.get('lms_name') == 'RUSL']
        
        # OUSL Activities
        if ousl_activities:
            ousl_header = Paragraph("OUSL (Open University of Sri Lanka)", self.styles['SectionHeader'])
            story.append(ousl_header)
            self._add_activity_table(story, ousl_activities)
        
        # RUSL Activities
        if rusl_activities:
            rusl_header = Paragraph("RUSL (Rajarata University)", self.styles['SectionHeader'])
            story.append(rusl_header)
            self._add_activity_table(story, rusl_activities)
        
        story.append(Spacer(1, 0.2 * inch))
    
    def _add_activity_table(self, story: list, activities: List[Dict]):
        """Add activity table to the story."""
        # Table header
        data = [['Type', 'Course', 'Title', 'Posted']]
        
        # Activity rows
        for activity in activities[:20]:  # Limit to 20 activities per LMS
            activity_type = activity.get('activity_type', 'N/A')
            course = Paragraph(activity.get('course_name', 'N/A'), self.styles['CustomBody'])
            title = Paragraph(activity.get('title', 'N/A'), self.styles['CustomBody'])
            posted = self._format_datetime(activity.get('first_seen', 'N/A'))
            
            data.append([activity_type, course, title, posted])
        
        # Create table
        table = Table(data, colWidths=[0.8*inch, 1.8*inch, 2.5*inch, 1.3*inch])
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2 * inch))
    
    def _create_deadlines_section(self, story: list, deadlines: List[Dict]):
        """Create upcoming deadlines section."""
        if not deadlines:
            return
        
        # Filter deadlines for next 30 days
        now = datetime.now(timezone.utc)
        thirty_days = now + timedelta(days=30)
        
        upcoming = []
        for deadline in deadlines:
            try:
                deadline_date = datetime.fromisoformat(deadline.get('deadline_date', '').replace('Z', '+00:00'))
                if now <= deadline_date <= thirty_days:
                    upcoming.append(deadline)
            except:
                continue
        
        if not upcoming:
            return
        
        header = Paragraph(f"Upcoming Deadlines (Next 30 Days) - {len(upcoming)}", self.styles['CustomSubtitle'])
        story.append(header)
        
        # Sort by deadline date
        upcoming.sort(key=lambda x: x.get('deadline_date', ''))
        
        # Table header
        data = [['LMS', 'Title', 'Course', 'Deadline']]
        
        # Deadline rows
        for deadline in upcoming[:15]:  # Limit to 15 deadlines
            lms = deadline.get('lms_name', 'N/A')
            title = Paragraph(deadline.get('title', 'N/A'), self.styles['CustomBody'])
            course = Paragraph(deadline.get('course_name', '') or '-', self.styles['CustomBody'])
            deadline_date = self._format_datetime(deadline.get('deadline_date', 'N/A'))
            
            data.append([lms, title, course, deadline_date])
        
        # Create table
        table = Table(data, colWidths=[0.6*inch, 2.2*inch, 2*inch, 1.6*inch])
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff3cd')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fffef0')]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2 * inch))
    
    def _create_footer(self, story: list):
        """Create report footer."""
        story.append(Spacer(1, 0.5 * inch))
        
        footer_text = """
        <i>This report was automatically generated by LMS Activity Monitor.<br/>
        For more information, visit the dashboard at:</i><br/>
        <b>https://lms-activity-monitor.up.railway.app</b>
        """
        footer = Paragraph(footer_text, self.styles['CustomBody'])
        story.append(footer)
    
    def generate_report(self, activities: List[Dict], deadlines: List[Dict], stats: Dict) -> str:
        """
        Generate PDF report with activities and deadlines.
        
        Args:
            activities: List of new activities
            deadlines: List of upcoming deadlines
            stats: Statistics dictionary
        
        Returns:
            Path to the generated PDF file
        """
        # Generate filename with timestamp
        current_time = self._get_colombo_time()
        filename = f"LMS_Report_{current_time.strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Build story
        story = []
        
        # Add sections
        self._create_header(story)
        self._create_summary_section(story, stats)
        self._create_activities_section(story, activities)
        self._create_deadlines_section(story, deadlines)
        self._create_footer(story)
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ PDF report generated: {filepath}")
        return filepath


if __name__ == "__main__":
    # Test PDF generation
    from database import Database
    
    db = Database()
    generator = PDFReportGenerator()
    
    # Get data
    new_activities = db.get_new_activities()
    upcoming_deadlines = db.get_all_upcoming_deadlines(days_ahead=30)
    stats = db.get_stats()
    
    # Generate report
    pdf_path = generator.generate_report(new_activities, upcoming_deadlines, stats)
    print(f"PDF report saved to: {pdf_path}")
