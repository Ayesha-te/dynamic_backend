import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from django.core.files.base import ContentFile
import re


def strip_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def generate_blog_pdf(blog):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1f2937',
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#6b7280',
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    excerpt_style = ParagraphStyle(
        'Excerpt',
        parent=styles['Normal'],
        fontSize=12,
        textColor='#374151',
        spaceAfter=15,
        alignment=TA_JUSTIFY,
        fontName='Helvetica-BoldOblique'
    )
    
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#1f2937',
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        leading=14,
        fontName='Helvetica'
    )
    
    story = []
    
    story.append(Paragraph(blog.title, title_style))
    
    date_str = blog.created_at.strftime('%B %d, %Y')
    meta_text = f"Published on {date_str}"
    story.append(Paragraph(meta_text, meta_style))
    
    story.append(Spacer(1, 0.3 * inch))
    
    if blog.excerpt:
        story.append(Paragraph(blog.excerpt, excerpt_style))
        story.append(Spacer(1, 0.2 * inch))
    
    if blog.content:
        clean_content = strip_html_tags(blog.content)
        content_paragraphs = clean_content.split('\n\n')
        
        for para_text in content_paragraphs:
            if para_text.strip():
                story.append(Paragraph(para_text.strip(), content_style))
                story.append(Spacer(1, 0.1 * inch))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def save_blog_as_pdf(blog):
    pdf_buffer = generate_blog_pdf(blog)
    
    filename = f"blog_{blog.slug}.pdf"
    pdf_content = ContentFile(pdf_buffer.read(), name=filename)
    
    blog.pdf_file = pdf_content
    blog.pdf_type = 'auto'
    blog.save()
    
    return blog
