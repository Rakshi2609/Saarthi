import os
import sys
import io
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    # Load template
    template_path = 'template.pptx'
    prs = pptx.Presentation(template_path)
    
    # Extract background images from template
    cover_bg_blob = prs.slides[0].shapes[0].image.blob
    content_bg_blob = prs.slides[1].shapes[0].image.blob
    
    # Template image bounds
    bg_left = prs.slides[1].shapes[0].left
    bg_top = prs.slides[1].shapes[0].top
    bg_width = prs.slides[1].shapes[0].width
    bg_height = prs.slides[1].shapes[0].height
    
    cover_left = prs.slides[0].shapes[0].left
    cover_top = prs.slides[0].shapes[0].top
    cover_width = prs.slides[0].shapes[0].width
    cover_height = prs.slides[0].shapes[0].height
    
    blank_layout = prs.slide_layouts[4] # Blank
    
    # Colors
    NAVY = RGBColor(11, 37, 69)         # #0B2545
    GREEN = RGBColor(11, 138, 68)       # #0B8A44
    ORANGE = RGBColor(232, 93, 4)       # #E85D04
    DARK = RGBColor(15, 23, 42)         # #0F172A
    BODY = RGBColor(51, 65, 85)         # #334155
    MUTED = RGBColor(100, 116, 139)     # #64748B
    LIGHT_BG = RGBColor(248, 250, 252)  # #F8FAFC
    BORDER = RGBColor(226, 232, 240)    # #E2E8F0
    WHITE = RGBColor(255, 255, 255)
    GREEN_TINT = RGBColor(240, 253, 244)# #F0FDF4
    GREEN_BORDER = RGBColor(187, 247, 208)
    BLUE_TINT = RGBColor(239, 246, 255) # #EFF6FF
    BLUE_BORDER = RGBColor(191, 219, 254)
    AMBER_TINT = RGBColor(254, 243, 199) # #FEF3C7
    AMBER_BORDER = RGBColor(253, 230, 138)
    RED_TINT = RGBColor(254, 242, 242)
    RED_TEXT = RGBColor(185, 28, 28)

    # Helper: Clear existing shapes on a slide except background
    def clear_shapes_except_bg(slide):
        shapes_to_remove = [s for s in slide.shapes if s.shape_type != pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE]
        for s in shapes_to_remove:
            sp = s._element
            sp.getparent().remove(sp)

    # Helper: Add standard content slide header and footer
    def setup_content_slide(slide, category, title, subtitle, slide_num):
        # Header text frame
        header_box = slide.shapes.add_textbox(Inches(2.35), Inches(0.95), Inches(8.8), Inches(1.15))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0)
        tf.margin_top = Inches(0)
        tf.margin_right = Inches(0)
        tf.margin_bottom = Inches(0)
        
        # Category
        p0 = tf.paragraphs[0]
        p0.text = category.upper()
        p0.font.name = 'Calibri'
        p0.font.size = Pt(9.5)
        p0.font.bold = True
        p0.font.color.rgb = GREEN
        p0.space_after = Pt(2)
        
        # Title
        p1 = tf.add_paragraph()
        p1.text = title
        p1.font.name = 'Calibri'
        p1.font.size = Pt(20)
        p1.font.bold = True
        p1.font.color.rgb = NAVY
        p1.space_after = Pt(2)
        
        # Subtitle
        if subtitle:
            p2 = tf.add_paragraph()
            p2.text = subtitle
            p2.font.name = 'Calibri'
            p2.font.size = Pt(11)
            p2.font.color.rgb = MUTED
            
        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.6), Inches(7.4), Inches(8.5), Inches(0.3))
        ftf = footer_box.text_frame
        ftf.word_wrap = True
        ftf.margin_left = Inches(0)
        ftf.margin_top = Inches(0)
        fp = ftf.paragraphs[0]
        fp.text = "Saarthi · AI-Powered Smart Lending Decision Hub · TVS Credit EPIC 8"
        fp.font.name = 'Calibri'
        fp.font.size = Pt(8.5)
        fp.font.color.rgb = MUTED
        
        # Slide Number
        num_box = slide.shapes.add_textbox(Inches(9.8), Inches(7.4), Inches(1.3), Inches(0.3))
        ntf = num_box.text_frame
        ntf.margin_right = Inches(0)
        np = ntf.paragraphs[0]
        np.alignment = PP_ALIGN.RIGHT
        np.text = f"{slide_num}"
        np.font.name = 'Calibri'
        np.font.size = Pt(8.5)
        np.font.bold = True
        np.font.color.rgb = MUTED

    # Helper: Create card rectangle
    def add_card(slide, left, top, width, height, bg_color=LIGHT_BG, border_color=BORDER, shape_type=MSO_SHAPE.ROUNDED_RECTANGLE):
        shape = slide.shapes.add_shape(shape_type, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1)
        else:
            shape.line.fill.background()
        return shape

    # Helper: Add formatted text box inside card
    def add_card_text(slide, left, top, width, height, margin=0.12):
        tb = slide.shapes.add_textbox(left + Inches(margin), top + Inches(margin), width - Inches(2*margin), height - Inches(2*margin))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0)
        tf.margin_top = Inches(0)
        tf.margin_right = Inches(0)
        tf.margin_bottom = Inches(0)
        return tf

    # Function to add new slide from template
    def add_slide_from_template():
        s = prs.slides.add_slide(blank_layout)
        s.shapes.add_picture(io.BytesIO(content_bg_blob), bg_left, bg_top, bg_width, bg_height)
        return s

    # -------------------------------------------------------------
    # SLIDE 1: Title / Cover Slide
    # -------------------------------------------------------------
    s1 = prs.slides[0]
    clear_shapes_except_bg(s1)
    
    # Crisp white container card positioned inside the green area
    add_card(s1, Inches(0.8), Inches(1.45), Inches(5.4), Inches(4.9), bg_color=WHITE, border_color=BORDER)
    tf1 = add_card_text(s1, Inches(0.8), Inches(1.45), Inches(5.4), Inches(4.9), margin=0.22)
    
    # Badge
    p = tf1.paragraphs[0]
    p.text = "TVS CREDIT E.P.I.C 8 · ROUND 2 SUBMISSION"
    p.font.name = 'Calibri'
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(8)
    
    # Hindi + Brand Title
    p = tf1.add_paragraph()
    p.text = "सा Saarthi"
    p.font.name = 'Calibri'
    p.font.size = Pt(34)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(2)
    
    # Subtitle
    p = tf1.add_paragraph()
    p.text = "AI-Powered Smart Lending Decision Hub"
    p.font.name = 'Calibri'
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ORANGE
    p.space_after = Pt(12)
    
    # Tagline
    p = tf1.add_paragraph()
    p.text = "A 60-second, explainable, satellite-aware credit decision for rural and semi-urban India — purpose-built for TVS Credit."
    p.font.name = 'Calibri'
    p.font.size = Pt(11)
    p.font.color.rgb = BODY
    p.space_after = Pt(14)
    
    # Feature Pills
    features = [
        ("⚡ 60-Second TAT", "Instant credit & default scoring"),
        ("🛰️ Satellite NDVI", "Alternative data for thin-file farmers"),
        ("⚖️ RBI DLG 2025", "SHAP per-decision cards & 5% FLDG cap"),
        ("🤖 Multilingual GenAI", "Hindi-English conversational RAG")
    ]
    for tag, desc in features:
        p = tf1.add_paragraph()
        p.text = f"• {tag}: "
        p.font.name = 'Calibri'
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        run = p.add_run()
        run.text = desc
        run.font.name = 'Calibri'
        run.font.size = Pt(9.5)
        run.font.bold = False
        run.font.color.rgb = BODY
        p.space_after = Pt(4)
        
    p = tf1.add_paragraph()
    p.text = "────────────────────────────────────────"
    p.font.name = 'Calibri'
    p.font.size = Pt(8)
    p.font.color.rgb = BORDER
    p.space_after = Pt(6)
    
    # Presenter info
    p = tf1.add_paragraph()
    p.text = "Team Saarthi · VIT Chennai | Rakshith Ganjimut (B.Tech CSE AI & Robotics)"
    p.font.name = 'Calibri'
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(2)
    
    p = tf1.add_paragraph()
    p.text = "Demo: http://localhost:5173  |  API Docs: http://localhost:8000/docs"
    p.font.name = 'Calibri'
    p.font.size = Pt(9)
    p.font.color.rgb = MUTED

    # -------------------------------------------------------------
    # SLIDE 2: What we'll cover in 4 minutes (Agenda)
    # -------------------------------------------------------------
    s2 = prs.slides[1]
    clear_shapes_except_bg(s2)
    setup_content_slide(s2, "Agenda & Executive Summary", "What we'll cover in 4 minutes", "A structured tour of the rural credit crisis, regulatory tailwinds, architecture, and live demo", 2)
    
    agenda_items = [
        ("1", "The Problem", "Why 9 in 10 landless farmers are locked out of formal credit — and the alternative data gap behind it.", AMBER_TINT, AMBER_BORDER),
        ("2", "Regulatory Tailwind", "RBI FREE-AI 7 Sutras, DLG 2025 (5% FLDG cap), and ₹2L collateral-free agri lending cap.", BLUE_TINT, BLUE_BORDER),
        ("3", "Market White Space", "Why Bajaj, Jio Financial, Airtel, and Credila are urban/salaried-first, leaving rural credit open.", GREEN_TINT, GREEN_BORDER),
        ("4", "What Saarthi Does", "4 integrated modules: Credit Scorer, Fraud Engine, Loan Recommender, and Multilingual GenAI Assistant.", LIGHT_BG, BORDER),
        ("5", "Evidence It Works", "IFPRI / KhetScore Odisha RCT validation: +20pp formal credit uptake with lower default.", LIGHT_BG, BORDER),
        ("6", "Live Production Demo", "Interactive 3-page web app: Apply form + SHAP explainer, Hindi-English chat, Underwriter Dashboard.", LIGHT_BG, BORDER),
    ]
    
    for i, (num, title, desc, bg, border) in enumerate(agenda_items):
        col = i % 2
        row = i // 2
        l = Inches(0.6 + col * 5.3)
        t = Inches(2.15 + row * 1.6)
        w = Inches(5.1)
        h = Inches(1.45)
        
        add_card(s2, l, t, w, h, bg_color=bg, border_color=border)
        
        # Number badge
        nb = add_card(s2, l + Inches(0.18), t + Inches(0.2), Inches(0.55), Inches(0.55), bg_color=NAVY if i < 3 else GREEN, border_color=None)
        ntf = nb.text_frame
        np = ntf.paragraphs[0]
        np.alignment = PP_ALIGN.CENTER
        np.text = num
        np.font.name = 'Calibri'
        np.font.size = Pt(16)
        np.font.bold = True
        np.font.color.rgb = WHITE
        
        # Text inside card
        tf = add_card_text(s2, l + Inches(0.85), t + Inches(0.12), w - Inches(0.95), h - Inches(0.24), margin=0)
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = 'Calibri'
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(3)
        
        p = tf.add_paragraph()
        p.text = desc
        p.font.name = 'Calibri'
        p.font.size = Pt(10)
        p.font.color.rgb = BODY

    # -------------------------------------------------------------
    # SLIDE 3: The Rural Credit Problem
    # -------------------------------------------------------------
    s3 = add_slide_from_template()
    setup_content_slide(s3, "Problem Statement & Industry Context", "Rural India needs a different credit decision", "9 in 10 landless farmers are locked out of formal credit. The traditional status-quo takes 2–4 weeks.", 3)
    
    # Top 4 Stat Cards
    stats = [
        ("9.5%", "Landless KCC Access", "Only 9.5% of landless rural households possess a Kisan Credit Card (KCC).", RED_TINT, RED_TEXT),
        ("30.1%", "Marginal Farmer KCC", "Only 30.1% of marginal farmers (<0.4 ha) have formal institutional credit.", AMBER_TINT, ORANGE),
        ("23.4%", "Moneylender Reliance", "23.4% of rural households still rely on non-institutional lenders (36–60% interest).", RED_TINT, RED_TEXT),
        ("2–4 Wks", "Status-Quo TAT", "Average turnaround time for rural two-wheeler / tractor credit approvals today.", BLUE_TINT, NAVY)
    ]
    for i, (val, label, detail, bg, val_col) in enumerate(stats):
        l = Inches(0.6 + i * 2.68)
        t = Inches(2.15)
        w = Inches(2.55)
        h = Inches(1.85)
        add_card(s3, l, t, w, h, bg_color=bg, border_color=BORDER)
        tf = add_card_text(s3, l, t, w, h, margin=0.15)
        
        p = tf.paragraphs[0]
        p.text = val
        p.font.name = 'Calibri'
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = val_col
        p.space_after = Pt(2)
        
        p = tf.add_paragraph()
        p.text = label
        p.font.name = 'Calibri'
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = DARK
        p.space_after = Pt(3)
        
        p = tf.add_paragraph()
        p.text = detail
        p.font.name = 'Calibri'
        p.font.size = Pt(8.5)
        p.font.color.rgb = BODY

    # Bottom Insights Card
    add_card(s3, Inches(0.6), Inches(4.15), Inches(10.6), Inches(2.7), bg_color=LIGHT_BG, border_color=BORDER)
    tf3 = add_card_text(s3, Inches(0.6), Inches(4.15), Inches(10.6), Inches(2.7), margin=0.2)
    
    p = tf3.paragraphs[0]
    p.text = "THE ROOT CAUSE & THE SAARTHI INSIGHT (NABARD NAFIS 2021–22 Benchmarks)"
    p.font.name = 'Calibri'
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(6)
    
    insights = [
        ("Bureau-first credit scoring fails rural India: ", "CIBIL / Experian history is missing or stale for >60% of tractor and two-wheeler loan applicants in Tier-3/4 towns."),
        ("The alternative data exists today: ", "Satellite vegetation indices (Sentinel-2 NDVI), IMD rainfall deviation, crop cycles, land records, and local transaction proxies are accessible."),
        ("The integration gap: ", "No NBFC platform has wired satellite, agri-socio signals, and fraud rules into an automated, explainable decision engine that an underwriter can approve in 60 seconds."),
        ("The business opportunity for TVS Credit: ", "Expand rural credit disbursement by 20–30% with lower default rates by underwriting the creditworthy 'invisible' population.")
    ]
    for bullet_title, bullet_desc in insights:
        p = tf3.add_paragraph()
        p.text = "▸ " + bullet_title
        p.font.name = 'Calibri'
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        run = p.add_run()
        run.text = bullet_desc
        run.font.name = 'Calibri'
        run.font.size = Pt(9.5)
        run.font.bold = False
        run.font.color.rgb = BODY
        p.space_after = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 4: Regulatory Tailwind
    # -------------------------------------------------------------
    s4 = add_slide_from_template()
    setup_content_slide(s4, "Regulatory Compliance & Mandates", "The regulator is on our side", "RBI's FREE-AI 7 Sutras, DLG 2025, and the ₹2L collateral-free cap create a massive tailwind for Saarthi", 4)
    
    reg_cards = [
        ("RBI FREE-AI 7 Sutras", "Aug 13, 2025 · RBI Framework", "Mandates Explainable AI (XAI) for credit appraisal, strict bias and fairness auditing across demographics, human-in-the-loop controls, and indigenous language accessibility. Black-box credit models face severe scrutiny.", BLUE_TINT, BLUE_BORDER),
        ("DLG 2025 — 5% FLDG Cap", "May 8, 2025 · Digital Lending Directions", "Caps First Loss Default Guarantee (FLDG) at 5% of digital lending portfolios. Crucially mandates: 'DLG shall not act as a substitute for credit appraisal.' Real algorithmic underwriting rigor is now a strict legal minimum.", GREEN_TINT, GREEN_BORDER),
        ("₹2 Lakh Collateral-Free Agri Limit", "Dec 6, 2024 · RBI FIDD", "Raised the collateral-free agri-loan limit from ₹1.6L to ₹2.0L. The central bank is actively expanding unsecured small-ticket rural credit — exactly where bureau data is absent and alternative scoring is vital.", AMBER_TINT, AMBER_BORDER),
        ("Mandatory CIMS Registration & KFS", "Jun 15, 2025 · Compliance Deadline", "Requires all Digital Lending Apps (DLAs) to register on RBI's CIMS portal, auto-generate standard Key Fact Statements (KFS), enforce a 1-day cooling-off period, and maintain immutable decision audit logs.", LIGHT_BG, BORDER)
    ]
    
    for i, (title, date_tag, desc, bg, border) in enumerate(reg_cards):
        col = i % 2
        row = i // 2
        l = Inches(0.6 + col * 5.3)
        t = Inches(2.15 + row * 2.4)
        w = Inches(5.1)
        h = Inches(2.25)
        
        add_card(s4, l, t, w, h, bg_color=bg, border_color=border)
        tf = add_card_text(s4, l, t, w, h, margin=0.18)
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = 'Calibri'
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(2)
        
        p = tf.add_paragraph()
        p.text = date_tag
        p.font.name = 'Calibri'
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = GREEN
        p.space_after = Pt(6)
        
        p = tf.add_paragraph()
        p.text = desc
        p.font.name = 'Calibri'
        p.font.size = Pt(9.5)
        p.font.color.rgb = BODY

    # -------------------------------------------------------------
    # SLIDE 5: Competitive Landscape Table
    # -------------------------------------------------------------
    s5 = add_slide_from_template()
    setup_content_slide(s5, "Competitive Positioning & White Space", "Nobody in the market is doing this", "Bajaj, Jio Financial, Airtel, and Credila are GenAI-first — but every one of them is urban and salaried-first", 5)
    
    # Comparison Table
    rows = 7
    cols = 6
    left = Inches(0.6)
    top = Inches(2.15)
    width = Inches(10.6)
    height = Inches(4.7)
    
    table_shape = s5.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    
    table.columns[0].width = Inches(2.1)
    table.columns[1].width = Inches(1.7)
    table.columns[2].width = Inches(1.7)
    table.columns[3].width = Inches(1.7)
    table.columns[4].width = Inches(1.7)
    table.columns[5].width = Inches(1.7)
    
    headers = ["Dimension", "Bajaj Finance", "Jio Financial", "Airtel Finance", "HDFC Credila", "Saarthi (Ours)"]
    table_data = [
        ["Target Segment", "Urban salaried", "UPI / mobile users", "Telco thin-file", "Students (abroad)", "Rural & semi-urban farmers / gig"],
        ["Core Data Signal", "Salary slips, CIBIL", "UPI & wallet txns", "Recharge & device", "Admission letter", "Satellite NDVI, Weather, Land & Agri"],
        ["GenAI Assistant", "Yes (10k loans/mo)", "Yes (130 agents)", "Yes (telco bot)", "Yes (Basic FAQ)", "Yes (Hindi-English + Tool Calling)"],
        ["Satellite / Agri Credit", "❌ None", "❌ None", "❌ None", "❌ None", "✓ Sentinel-2 NDVI + IMD Weather"],
        ["RBI DLG-2025 Ready", "Partial (Bureau)", "Partial (Closed)", "Partial", "Partial", "✓ (KFS, SHAP Log, Bias Audit)"],
        ["First Decision TAT", "Days", "Minutes (Pre-approved)", "Minutes", "Days", "< 60 Seconds (Explainable)"]
    ]
    
    # Style Header
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.text = h_text
        cell.fill.solid()
        cell.fill.fore_color.rgb = GREEN if c_idx == 5 else NAVY
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.font.name = 'Calibri'
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        
    # Style Data Rows
    for r_idx, row_data in enumerate(table_data):
        for c_idx, val in enumerate(row_data):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = val
            cell.fill.solid()
            if c_idx == 5:
                cell.fill.fore_color.rgb = GREEN_TINT
            elif r_idx % 2 == 1:
                cell.fill.fore_color.rgb = LIGHT_BG
            else:
                cell.fill.fore_color.rgb = WHITE
                
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if c_idx == 0 else PP_ALIGN.CENTER
            p.font.name = 'Calibri'
            p.font.size = Pt(9.5)
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = NAVY
            elif c_idx == 5:
                p.font.bold = True
                p.font.color.rgb = GREEN if "✓" in val or "<" in val else NAVY
            else:
                p.font.color.rgb = RED_TEXT if "❌" in val else BODY

    # -------------------------------------------------------------
    # SLIDE 6: Evidence it Works - IFPRI RCT
    # -------------------------------------------------------------
    s6 = add_slide_from_template()
    setup_content_slide(s6, "Empirical Validation & Benchmark", "It already works — IFPRI / KhetScore Odisha RCT", "The only published end-to-end satellite credit trial proves the model. Saarthi brings it to production.", 6)
    
    # Left Card: The Academic Evidence
    add_card(s6, Inches(0.6), Inches(2.15), Inches(5.1), Inches(4.7), bg_color=BLUE_TINT, border_color=BLUE_BORDER)
    tf6_l = add_card_text(s6, Inches(0.6), Inches(2.15), Inches(5.1), Inches(4.7), margin=0.2)
    
    p = tf6_l.paragraphs[0]
    p.text = "THE PUBLISHED BENCHMARK"
    p.font.name = 'Calibri'
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(2)
    
    p = tf6_l.add_paragraph()
    p.text = "IFPRI Discussion Paper 2288 (2024)"
    p.font.name = 'Calibri'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(8)
    
    # Stat callout
    p = tf6_l.add_paragraph()
    p.text = "+20 percentage points"
    p.font.name = 'Calibri'
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(2)
    
    p = tf6_l.add_paragraph()
    p.text = "increase in formal-credit uptake in treatment villages"
    p.font.name = 'Calibri'
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = DARK
    p.space_after = Pt(8)
    
    rct_points = [
        "58 villages in Odisha: 29 treatment, 29 control across multiple seasons.",
        "Farmers underwritten using satellite NDVI scores borrowed MORE institutional credit.",
        "Crucially, treated households were LESS likely to report loan repayment distress.",
        "Trial successfully scaled from 50 initial farmers to 15,000 farmers."
    ]
    for pt in rct_points:
        p = tf6_l.add_paragraph()
        p.text = "• " + pt
        p.font.name = 'Calibri'
        p.font.size = Pt(9.5)
        p.font.color.rgb = BODY
        p.space_after = Pt(4)

    # Right Card: What Saarthi Adds
    add_card(s6, Inches(5.9), Inches(2.15), Inches(5.3), Inches(4.7), bg_color=GREEN_TINT, border_color=GREEN_BORDER)
    tf6_r = add_card_text(s6, Inches(5.9), Inches(2.15), Inches(5.3), Inches(4.7), margin=0.2)
    
    p = tf6_r.paragraphs[0]
    p.text = "WHAT SAARTHI ADDS FOR PRODUCTION SCALE"
    p.font.name = 'Calibri'
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(2)
    
    p = tf6_r.add_paragraph()
    p.text = "From Academic Pilot to Enterprise Platform"
    p.font.name = 'Calibri'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)
    
    additions = [
        ("Live Dynamic Re-scoring: ", "Continuous weather & NDVI monitoring instead of static once-a-year scoring."),
        ("Integrated Fraud Defense: ", "Hybrid heuristic rules + Isolation Forest anomaly detection for device/identity fraud."),
        ("Multilingual GenAI Assistant: ", "Hindi-English conversational interface with function calling for credit assessment."),
        ("Underwriter Command Center: ", "Real-time India risk heatmap, portfolio KPIs, and application drill-down."),
        ("Full XAI & DLG-2025 Audit Trail: ", "Per-decision TreeExplainer SHAP reason codes and compliance logs."),
        ("Loan Recommendation Engine: ", "Optimizes loan ticket size, interest rate, and tenure capped at 5% FLDG risk.")
    ]
    for h_text, d_text in additions:
        p = tf6_r.add_paragraph()
        p.text = "✓ " + h_text
        p.font.name = 'Calibri'
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        run = p.add_run()
        run.text = d_text
        run.font.name = 'Calibri'
        run.font.size = Pt(9.5)
        run.font.bold = False
        run.font.color.rgb = BODY
        p.space_after = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 7: 4 Integrated Modules
    # -------------------------------------------------------------
    s7 = add_slide_from_template()
    setup_content_slide(s7, "System Architecture & Product Modules", "4 integrated modules in 1 product", "Engineered on FastAPI + XGBoost + SHAP + Gemini Flash + Leaflet Geospatial Engine", 7)
    
    modules = [
        ("1", "AI Credit Scorer", "XGBoost Regressor (300–900)", "R² 0.85 holdout accuracy", [
            "Inputs: Income, land acres, NDVI productivity, rainfall anomaly, livestock assets, KYC tier.",
            "Outputs: Credit score (300-900), default risk %, loan approval decision, and top-3 SHAP drivers."
        ], BLUE_TINT, BLUE_BORDER),
        ("2", "Fraud Engine", "Rule-Engine + Isolation Forest", "Catches 6 signal classes", [
            "Signals: Velocity spikes, geo-mismatch, disposable email, shared device IDs, SIM age anomalies.",
            "Outputs: Risk score, anomaly flag, and human-in-the-loop review trigger."
        ], RED_TINT, BORDER),
        ("3", "GenAI Assistant", "Gemini 1.5 Flash + RAG", "4 TVS Docs + DLG 2025", [
            "Hindi-English chat with function-calling to execute live credit scoring & EMI estimates.",
            "Includes zero-key offline rule-based fallback ensuring 100% uptime without external API."
        ], GREEN_TINT, GREEN_BORDER),
        ("4", "Underwriter Hub", "SPA + Leaflet Geospatial", "Live Heatmap + 4 KPIs", [
            "Interactive India state risk heatmap, live WebSocket application feed, applicant drill-down.",
            "Replaces manual 4-hour morning branch spreadsheet reviews with a 60-second workflow."
        ], AMBER_TINT, AMBER_BORDER)
    ]
    
    for i, (num, name, tech, metric, points, bg, border) in enumerate(modules):
        col = i % 2
        row = i // 2
        l = Inches(0.6 + col * 5.3)
        t = Inches(2.15 + row * 2.4)
        w = Inches(5.1)
        h = Inches(2.25)
        
        add_card(s7, l, t, w, h, bg_color=bg, border_color=border)
        
        # Number Badge
        nb = add_card(s7, l + Inches(0.18), t + Inches(0.18), Inches(0.45), Inches(0.45), bg_color=NAVY, border_color=None)
        ntf = nb.text_frame
        np = ntf.paragraphs[0]
        np.alignment = PP_ALIGN.CENTER
        np.text = num
        np.font.name = 'Calibri'
        np.font.size = Pt(14)
        np.font.bold = True
        np.font.color.rgb = WHITE
        
        # Module Info
        tf = add_card_text(s7, l + Inches(0.72), t + Inches(0.14), w - Inches(0.85), h - Inches(0.24), margin=0)
        p = tf.paragraphs[0]
        p.text = name
        p.font.name = 'Calibri'
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(1)
        
        p = tf.add_paragraph()
        p.text = f"{tech}  |  {metric}"
        p.font.name = 'Calibri'
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = GREEN
        p.space_after = Pt(4)
        
        for pt in points:
            p = tf.add_paragraph()
            p.text = "• " + pt
            p.font.name = 'Calibri'
            p.font.size = Pt(8.5)
            p.font.color.rgb = BODY
            p.space_after = Pt(2)

    # -------------------------------------------------------------
    # SLIDE 8: ML Performance & Training Data
    # -------------------------------------------------------------
    s8 = add_slide_from_template()
    setup_content_slide(s8, "Machine Learning Validation & Metrics", "Trained on 5,000 synthetic applicants · Live now", "The full ML pipeline runs end-to-end on demo data in < 2 seconds per applicant", 8)
    
    # 4 Metric Cards
    kpis = [
        ("0.98", "Default Classifier AUC", "XGBoost classifier on 5,000 rows (80/20 holdout split)", GREEN_TINT, GREEN),
        ("55 pts", "Credit-Score MAE", "Mean Absolute Error on 300–900 CIBIL-equivalent scale", BLUE_TINT, NAVY),
        ("6 Classes", "Fraud Signal Detection", "Velocity, geo mismatch, device sharing, disposable contact", RED_TINT, RED_TEXT),
        ("< 2 sec", "End-to-End Latency", "From form submission to credit score + SHAP + loan recommendation", AMBER_TINT, ORANGE)
    ]
    for i, (val, title, sub, bg, val_col) in enumerate(kpis):
        l = Inches(0.6 + i * 2.68)
        t = Inches(2.15)
        w = Inches(2.55)
        h = Inches(1.85)
        add_card(s8, l, t, w, h, bg_color=bg, border_color=BORDER)
        tf = add_card_text(s8, l, t, w, h, margin=0.15)
        
        p = tf.paragraphs[0]
        p.text = val
        p.font.name = 'Calibri'
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = val_col
        p.space_after = Pt(2)
        
        p = tf.add_paragraph()
        p.text = title
        p.font.name = 'Calibri'
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = DARK
        p.space_after = Pt(3)
        
        p = tf.add_paragraph()
        p.text = sub
        p.font.name = 'Calibri'
        p.font.size = Pt(8.5)
        p.font.color.rgb = BODY

    # Bottom Detailed Box
    add_card(s8, Inches(0.6), Inches(4.15), Inches(10.6), Inches(2.7), bg_color=LIGHT_BG, border_color=BORDER)
    tf8 = add_card_text(s8, Inches(0.6), Inches(4.15), Inches(10.6), Inches(2.7), margin=0.2)
    
    p = tf8.paragraphs[0]
    p.text = "TRAINING DATA CHARACTERISTICS & EXPLAINABILITY ENGINE"
    p.font.name = 'Calibri'
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(6)
    
    data_points = [
        ("Representative Dataset: ", "5,000 synthetic Indian loan applicants modeled after NABARD NAFIS 2021–22 distributions across 13 states, 24 districts, 9 loan products, and 7 employment profiles."),
        ("Realistic Risk Distribution: ", "Baseline 70% approve / 20% refer / 10% reject; mean CIBIL 645 ± 70 with simulated thin-file rural profiles."),
        ("Agricultural Feature Engineering: ", "9 crop types, NDVI range 0.30–0.95, rainfall deficit % from IMD normals, land size 0.5–12.0 acres, livestock count, and irrigation access."),
        ("Production TreeExplainer SHAP: ", "Computes exact Shapley values in real-time, surfacing the top-3 positive/negative driver reason codes directly in English and Hindi for underwriters and customers.")
    ]
    for title_pt, desc_pt in data_points:
        p = tf8.add_paragraph()
        p.text = "▸ " + title_pt
        p.font.name = 'Calibri'
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        run = p.add_run()
        run.text = desc_pt
        run.font.name = 'Calibri'
        run.font.size = Pt(9.5)
        run.font.bold = False
        run.font.color.rgb = BODY
        p.space_after = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 9: Live Demo 3 Pages
    # -------------------------------------------------------------
    s9 = add_slide_from_template()
    setup_content_slide(s9, "Live Application Architecture", "Live demo · 3 pages, 4 minutes", "Seamless single-page application connecting customer onboarding, GenAI advisory, and underwriter operations", 9)
    
    pages = [
        ("PAGE 1: /apply", "Loan Application & Real-Time Scoring", [
            "Customer / dealer completes intuitive 12-field form (income, loan type, land size, crop type, location).",
            "Loads pre-configured demo presets (e.g., landless farmer, smallholder, rural artisan).",
            "Instant score gauge with top-3 SHAP positive & negative drivers.",
            "Recommended loan amount, tenure, interest rate, and monthly EMI calculation."
        ], BLUE_TINT, BLUE_BORDER),
        ("PAGE 2: /assistant", "Saarthi Multilingual Conversational AI", [
            "Bilingual natural language assistant (Hindi + English) powered by Gemini 1.5 Flash.",
            "Function calling / tool use: dynamically queries credit engine to fetch applicant score & EMI options.",
            "Grounded in real TVS Credit product guidelines (Two-Wheeler, Tractor, Gold Loan, DLG 2025).",
            "Built-in rule-based offline fallback guarantees zero failure when offline."
        ], GREEN_TINT, GREEN_BORDER),
        ("PAGE 3: /dashboard", "Underwriter Command Center", [
            "Interactive India choropleth risk heatmap displaying state-level approval rates & risk tiers.",
            "4 key portfolio health cards: Total Volume, Approval Rate, Average Score, High Risk Flags.",
            "Live streaming transaction feed simulating real-time applicant scoring every 3 seconds.",
            "Applicant drill-down modal showing full audit trail and anomaly breakdowns."
        ], AMBER_TINT, AMBER_BORDER)
    ]
    
    for i, (tag, title, bullets, bg, border) in enumerate(pages):
        l = Inches(0.6 + i * 3.6)
        t = Inches(2.15)
        w = Inches(3.4)
        h = Inches(4.7)
        
        add_card(s9, l, t, w, h, bg_color=bg, border_color=border)
        tf = add_card_text(s9, l, t, w, h, margin=0.18)
        
        p = tf.paragraphs[0]
        p.text = tag
        p.font.name = 'Calibri'
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = GREEN
        p.space_after = Pt(2)
        
        p = tf.add_paragraph()
        p.text = title
        p.font.name = 'Calibri'
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(8)
        
        for b in bullets:
            p = tf.add_paragraph()
            p.text = "• " + b
            p.font.name = 'Calibri'
            p.font.size = Pt(9)
            p.font.color.rgb = BODY
            p.space_after = Pt(5)

    # -------------------------------------------------------------
    # SLIDE 10: Regulatory Alignment with FREE-AI 7 Sutras
    # -------------------------------------------------------------
    s10 = add_slide_from_template()
    setup_content_slide(s10, "Regulatory Governance & Compliance", "Built for the regulator, not just the demo", "Saarthi is born-DLG-2025-compliant and rigorously mapped against RBI's FREE-AI 7 Sutras", 10)
    
    rows = 8
    cols = 3
    left = Inches(0.6)
    top = Inches(2.15)
    width = Inches(10.6)
    height = Inches(4.7)
    
    table_shape = s10.shapes.add_table(rows, cols, left, top, width, height)
    t10 = table_shape.table
    t10.columns[0].width = Inches(2.2)
    t10.columns[1].width = Inches(1.8)
    t10.columns[2].width = Inches(6.6)
    
    headers10 = ["RBI FREE-AI Sutra", "Principle Focus", "How Saarthi Implements It in Production"]
    sutras = [
        ("1. Trust", "Auditability & Integrity", "Immutable decision log per applicant; model card stored on disk; every score 100% reproducible with logged input feature snapshots."),
        ("2. People First", "Accessibility & Inclusion", "Hindi-English conversational UI designed for rural borrowers and branch loan officers; zero English-only financial jargon."),
        ("3. Innovation over Restraint", "Pragmatic Architecture", "Interpretable XGBoost + TreeExplainer SHAP chosen over opaque deep neural networks; simple, robust, and auditable."),
        ("4. Fairness & Equity", "Demographic Non-Bias", "Automated bias audits across age, gender, state, and employment tier; stratified metrics ensure parity in loan approval rates."),
        ("5. Accountability", "Model Governance", "Every model checkpoint, training dataset, and rule weight saved with SHA-256 hash; complete rollback and governance trail."),
        ("6. Understandability", "Explainable AI (XAI)", "Top-3 SHAP positive & negative reason codes surfaced to underwriters in English and to customers in Hindi."),
        ("7. Safety & Resilience", "High Availability & Guardrails", "Offline rule-based fallback for chat and scoring guarantees 100% service uptime even if LLM APIs are unreachable.")
    ]
    
    for c_idx, h_text in enumerate(headers10):
        cell = t10.cell(0, c_idx)
        cell.text = h_text
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        p.font.name = 'Calibri'
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = WHITE
        
    for r_idx, (sutra, focus, impl) in enumerate(sutras):
        c0 = t10.cell(r_idx + 1, 0)
        c0.text = sutra
        c0.fill.solid()
        c0.fill.fore_color.rgb = GREEN_TINT if r_idx % 2 == 1 else WHITE
        p = c0.text_frame.paragraphs[0]
        p.font.name = 'Calibri'
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        c1 = t10.cell(r_idx + 1, 1)
        c1.text = focus
        c1.fill.solid()
        c1.fill.fore_color.rgb = GREEN_TINT if r_idx % 2 == 1 else WHITE
        p = c1.text_frame.paragraphs[0]
        p.font.name = 'Calibri'
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = GREEN
        
        c2 = t10.cell(r_idx + 1, 2)
        c2.text = impl
        c2.fill.solid()
        c2.fill.fore_color.rgb = GREEN_TINT if r_idx % 2 == 1 else WHITE
        p = c2.text_frame.paragraphs[0]
        p.font.name = 'Calibri'
        p.font.size = Pt(9)
        p.font.color.rgb = BODY

    # -------------------------------------------------------------
    # SLIDE 11: Roadmap
    # -------------------------------------------------------------
    s11 = add_slide_from_template()
    setup_content_slide(s11, "Strategic Execution & Growth", "Roadmap · from Round 3 demo to RBI sandbox", "A disciplined 12-month commercialization and compliance roadmap for TVS Credit partnership", 11)
    
    phases = [
        ("PHASE 1 (NOW)", "Round 2 & 3 MVP Demo", "August 2026", [
            "5,000 synthetic applicants with realistic rural distributions.",
            "FastAPI backend with 7 production endpoints & Swagger docs.",
            "Next.js single-page application: Apply / Assistant / Dashboard.",
            "Gemini 1.5 Flash function calling + offline rule fallback."
        ], BLUE_TINT, BLUE_BORDER),
        ("PHASE 2 (MONTHS 1-3)", "NBFC Branch Pilot", "Q4 2026", [
            "Swap synthetic dataset with anonymized TVS Credit LMS extract.",
            "Integrate live bureau pull (CIBIL/Experian) + Aadhaar eKYC.",
            "Connect live Sentinel-2 NDVI satellite & IMD weather APIs.",
            "Field test in 1 district across 5 dealer branches (Target TAT < 30m)."
        ], GREEN_TINT, GREEN_BORDER),
        ("PHASE 3 (MONTHS 4-6)", "RBI Regulatory Sandbox", "Q1 2027", [
            "Submit application for RBI's On-Tap Regulatory Sandbox (DLG track).",
            "Expand assistant to Tamil, Telugu, Marathi, and Kannada.",
            "Comprehensive third-party bias and fairness validation.",
            "Automated Model Governance Card per RBI Sutra 7."
        ], AMBER_TINT, AMBER_BORDER),
        ("PHASE 4 (MONTHS 7-12)", "Scale to ₹500 Cr AUM", "Q3 2027", [
            "Scale across 10 NBFC partner networks in 5 rural states.",
            "Graph ML co-borrower network fraud ring detection.",
            "Automated weekly portfolio re-scoring and early default alerts.",
            "Open API gateway for co-lending partner banks and BCs."
        ], LIGHT_BG, BORDER)
    ]
    
    for i, (phase_tag, title, timeline, bullets, bg, border) in enumerate(phases):
        l = Inches(0.6 + i * 2.68)
        t = Inches(2.15)
        w = Inches(2.55)
        h = Inches(4.7)
        
        add_card(s11, l, t, w, h, bg_color=bg, border_color=border)
        tf = add_card_text(s11, l, t, w, h, margin=0.15)
        
        p = tf.paragraphs[0]
        p.text = phase_tag
        p.font.name = 'Calibri'
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = GREEN
        p.space_after = Pt(2)
        
        p = tf.add_paragraph()
        p.text = title
        p.font.name = 'Calibri'
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(2)
        
        p = tf.add_paragraph()
        p.text = timeline
        p.font.name = 'Calibri'
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = MUTED
        p.space_after = Pt(6)
        
        for b in bullets:
            p = tf.add_paragraph()
            p.text = "• " + b
            p.font.name = 'Calibri'
            p.font.size = Pt(8.5)
            p.font.color.rgb = BODY
            p.space_after = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 12: Team & The Ask
    # -------------------------------------------------------------
    s12 = add_slide_from_template()
    setup_content_slide(s12, "Team Credentials & TVS Credit Collaboration", "The ask · the team · the next 4 minutes", "We are seeking 1 NBFC partner, 1 district of loan officers, and 30 days of pilot data", 12)
    
    # Left Column: Why Us
    add_card(s12, Inches(0.6), Inches(2.15), Inches(5.1), Inches(4.7), bg_color=BLUE_TINT, border_color=BLUE_BORDER)
    tf12_l = add_card_text(s12, Inches(0.6), Inches(2.15), Inches(5.1), Inches(4.7), margin=0.2)
    
    p = tf12_l.paragraphs[0]
    p.text = "THE BUILDER"
    p.font.name = 'Calibri'
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(2)
    
    p = tf12_l.add_paragraph()
    p.text = "Rakshith Ganjimut · Team Saarthi"
    p.font.name = 'Calibri'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    
    team_points = [
        ("Academic Excellence: ", "B.Tech CSE (AI & Robotics) at VIT Chennai (2024–2028), CGPA 8.5."),
        ("Full-Stack & ML Engineering: ", "Production experience across FastAPI, Python, TypeScript, Next.js, and XGBoost/SHAP."),
        ("Proven SaaS Shipper: ", "Built and shipped AI Code Reviewer, Career Chatbot, and Task-Tapper."),
        ("Domain FinTech Experience: ", "BlackVolt intern — engineered real credit scoring models and pipelines for an operating NBFC."),
        ("Deep Rural Empathy: ", "Passionate about empowering Tier-3/4 India's 'invisible' credit population through alternative data.")
    ]
    for h_txt, b_txt in team_points:
        p = tf12_l.add_paragraph()
        p.text = "▸ " + h_txt
        p.font.name = 'Calibri'
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        run = p.add_run()
        run.text = b_txt
        run.font.name = 'Calibri'
        run.font.size = Pt(9.5)
        run.font.bold = False
        run.font.color.rgb = BODY
        p.space_after = Pt(8)

    # Right Column: The Ask
    add_card(s12, Inches(5.9), Inches(2.15), Inches(5.3), Inches(4.7), bg_color=GREEN_TINT, border_color=GREEN_BORDER)
    tf12_r = add_card_text(s12, Inches(5.9), Inches(2.15), Inches(5.3), Inches(4.7), margin=0.2)
    
    p = tf12_r.paragraphs[0]
    p.text = "THE ASK FOR TVS CREDIT"
    p.font.name = 'Calibri'
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(2)
    
    p = tf12_r.add_paragraph()
    p.text = "What We Need to Launch the Pilot"
    p.font.name = 'Calibri'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    
    ask_points = [
        ("30-Minute Working Session: ", "Meet with the TVS Credit Digital Lending leadership team to review pilot parameters."),
        ("1 Month Anonymized LMS Data: ", "~5,000 historical de-identified loan records to calibrate our alternative-data model on real TVS defaults."),
        ("1 District Dealer Pilot: ", "Pilot deployment with 5 rural two-wheeler / tractor dealer touchpoints in 1 district."),
        ("Regulatory Sandbox Sponsorship: ", "Partner sponsorship for joint submission to the RBI On-Tap Regulatory Sandbox."),
        ("Underwriter Mentorship: ", "2 hours/week feedback from a senior underwriter for 4 weeks to refine reason-code taxonomy.")
    ]
    for h_txt, b_txt in ask_points:
        p = tf12_r.add_paragraph()
        p.text = "✓ " + h_txt
        p.font.name = 'Calibri'
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        run = p.add_run()
        run.text = b_txt
        run.font.name = 'Calibri'
        run.font.size = Pt(9.5)
        run.font.bold = False
        run.font.color.rgb = BODY
        p.space_after = Pt(8)

    # -------------------------------------------------------------
    # SLIDE 13: Live Demo Script
    # -------------------------------------------------------------
    s13 = add_slide_from_template()
    setup_content_slide(s13, "Live Demonstration Guide", "Live demo · 4-minute walkthrough", "Follow this exact sequence during the live jury evaluation", 13)
    
    # 5 Demo Step Cards
    demo_steps = [
        ("0:00 – 0:45", "1. Dealer Loan Application", "Open #/apply as a dealer in Tamil Nadu. Fill 12 fields (or click 'Load Demo Applicant'). Watch instant score calculation (645), approval decision, and top-3 SHAP positive & negative drivers.", BLUE_TINT, NAVY),
        ("0:45 – 1:45", "2. Multilingual Assistant", "Switch to #/assistant. Ask in Hinglish: 'Will I get ₹3 lakh for a tractor in Madurai with 4.5 acres?' Assistant parses intent, calls live scoring tool, and returns loan terms, EMI, and required documents.", GREEN_TINT, GREEN),
        ("1:45 – 2:45", "3. Underwriter Command Hub", "Open #/dashboard. Review nationwide portfolio KPIs (avg score 645, 42.6% approval), interactive India risk heatmap by state, and real-time streaming applicant feed.", AMBER_TINT, ORANGE),
        ("2:45 – 3:30", "4. Fraud & DLG Audit Trail", "Click on a flagged high-risk application. Inspect Isolation Forest anomaly score, rule chips (geo mismatch, SIM age), and full DLG-2025 regulatory evidence trail.", RED_TINT, RED_TEXT),
        ("3:30 – 4:00", "5. Closing & Feedback", "Summarize 60-second decision TAT and compliance advantages. Open floor for jury questions and technical deep dive.", LIGHT_BG, NAVY)
    ]
    
    for i, (time_slot, step_title, step_desc, bg, col) in enumerate(demo_steps):
        t = Inches(2.15 + i * 0.95)
        l = Inches(0.6)
        w = Inches(10.6)
        h = Inches(0.85)
        
        add_card(s13, l, t, w, h, bg_color=bg, border_color=BORDER)
        
        # Time badge
        tb = add_card(s13, l + Inches(0.12), t + Inches(0.15), Inches(1.5), Inches(0.55), bg_color=col, border_color=None)
        ttf = tb.text_frame
        tp = ttf.paragraphs[0]
        tp.alignment = PP_ALIGN.CENTER
        tp.text = time_slot
        tp.font.name = 'Calibri'
        tp.font.size = Pt(11)
        tp.font.bold = True
        tp.font.color.rgb = WHITE
        
        # Step details
        tf = add_card_text(s13, l + Inches(1.75), t + Inches(0.08), w - Inches(1.85), h - Inches(0.16), margin=0)
        p = tf.paragraphs[0]
        p.text = step_title + ": "
        p.font.name = 'Calibri'
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        run = p.add_run()
        run.text = step_desc
        run.font.name = 'Calibri'
        run.font.size = Pt(9)
        run.font.bold = False
        run.font.color.rgb = BODY

    # -------------------------------------------------------------
    # SLIDE 14: Cover Response (Executive Briefing)
    # -------------------------------------------------------------
    s14 = add_slide_from_template()
    setup_content_slide(s14, "Official Cover Response", "Executive brief (200-word response)", "Official three-paragraph submission response for the TVS Credit E.P.I.C 8 evaluation portal", 14)
    
    paragraphs = [
        ("Problem & Context", "Roughly 9 in 10 landless Indian farmers and 7 in 10 marginal farmers have no formal credit history (NABARD NAFIS 2021–22), while rural credit decisioning takes 2–4 weeks. The data to solve this — satellite imagery, rainfall feeds, land records — exists, but has never been unified into an automated, explainable lending decision that an underwriter can execute in under 60 seconds.", RED_TINT, RED_TEXT),
        ("Regulatory & Market Insight", "Bureau-first credit scoring is the wrong tool for thin-file rural India. RBI's FREE-AI 7 Sutras and Digital Lending Directions 2025 explicitly mandate explainable AI and prohibit DLG substitution for underwriting rigour. Every major competitor (Bajaj, Jio Financial, Airtel, Credila) is urban-first and salaried-first, leaving rural satellite-credit entirely open.", BLUE_TINT, NAVY),
        ("Saarthi Solution & Proof", "Saarthi is a 4-module Smart Lending Decision Hub: XGBoost credit scoring with SHAP explainers, fraud anomaly detection, a Hindi-English GenAI assistant with function calling, and an underwriter dashboard with an India risk heatmap. Trained on 5,000 synthetic applicants, live now, RBI DLG-2025 ready, and built to deliver a 60-second explainable loan decision.", GREEN_TINT, GREEN)
    ]
    
    for i, (title, text, bg, border_col) in enumerate(paragraphs):
        t = Inches(2.15 + i * 1.55)
        l = Inches(0.6)
        w = Inches(10.6)
        h = Inches(1.45)
        
        add_card(s14, l, t, w, h, bg_color=bg, border_color=BORDER)
        tf = add_card_text(s14, l, t, w, h, margin=0.18)
        
        p = tf.paragraphs[0]
        p.text = f"{i+1}. {title}"
        p.font.name = 'Calibri'
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = border_col
        p.space_after = Pt(3)
        
        p = tf.add_paragraph()
        p.text = text
        p.font.name = 'Calibri'
        p.font.size = Pt(9.5)
        p.font.color.rgb = BODY

    # -------------------------------------------------------------
    # SLIDE 15: Conclusion & Thank You (Content Template Layout)
    # -------------------------------------------------------------
    s15 = add_slide_from_template()
    setup_content_slide(s15, "Submission Summary & Conclusion", "Thank you · Questions & discussion", "Saarthi is ready for deployment: 60-second TAT, DLG 2025 compliance, and proven satellite alternative scoring", 15)
    
    # Left Box: Summary of Impact
    add_card(s15, Inches(0.6), Inches(2.15), Inches(5.1), Inches(4.7), bg_color=GREEN_TINT, border_color=GREEN_BORDER)
    tf15_l = add_card_text(s15, Inches(0.6), Inches(2.15), Inches(5.1), Inches(4.7), margin=0.25)
    
    p = tf15_l.paragraphs[0]
    p.text = "SAARTHI VALUE PROPOSITION"
    p.font.name = 'Calibri'
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(4)
    
    p = tf15_l.add_paragraph()
    p.text = "The Digital Charioteer for Rural Inclusion"
    p.font.name = 'Calibri'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(12)
    
    summary_pillars = [
        ("⚡ 60-Second Credit TAT: ", "Transforms traditional 2–4 week manual loan appraisal into an automated 60-second decision."),
        ("🛰️ Satellite Alternative Scorer: ", "Overcomes the thin-file barrier for 90% of landless and marginal farmers with Sentinel-2 NDVI."),
        ("⚖️ Born DLG-2025 & FREE-AI Compliant: ", "Per-decision SHAP explainability cards, 5% FLDG cap enforcement, and immutable audit logs."),
        ("🤖 Vernacular GenAI Experience: ", "Accessible Hindi-English conversational interface with tool calling and grounded product RAG.")
    ]
    for h_txt, b_txt in summary_pillars:
        p = tf15_l.add_paragraph()
        p.text = h_txt
        p.font.name = 'Calibri'
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        run = p.add_run()
        run.text = b_txt
        run.font.name = 'Calibri'
        run.font.size = Pt(9.5)
        run.font.bold = False
        run.font.color.rgb = BODY
        p.space_after = Pt(6)

    # Right Box: Next Steps & Team Info
    add_card(s15, Inches(5.9), Inches(2.15), Inches(5.3), Inches(4.7), bg_color=BLUE_TINT, border_color=BLUE_BORDER)
    tf15_r = add_card_text(s15, Inches(5.9), Inches(2.15), Inches(5.3), Inches(4.7), margin=0.25)
    
    p = tf15_r.paragraphs[0]
    p.text = "SUBMISSION DETAILS & LIVE LINKS"
    p.font.name = 'Calibri'
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(4)
    
    p = tf15_r.add_paragraph()
    p.text = "Team Saarthi · VIT Chennai"
    p.font.name = 'Calibri'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(12)
    
    info_points = [
        ("Presenter: ", "Rakshith Ganjimut (B.Tech CSE AI & Robotics 2024–28)"),
        ("Source Repository: ", "github.com/Rakshi2609/Saarthi"),
        ("Interactive Frontend: ", "http://localhost:5173 (#/apply, #/assistant, #/dashboard)"),
        ("FastAPI Backend: ", "http://localhost:8000 (Interactive docs at /docs)"),
        ("Ready for Pilot: ", "1 district · 5 dealer branches · 30 days calibration")
    ]
    for h_txt, b_txt in info_points:
        p = tf15_r.add_paragraph()
        p.text = "▸ " + h_txt
        p.font.name = 'Calibri'
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        run = p.add_run()
        run.text = b_txt
        run.font.name = 'Calibri'
        run.font.size = Pt(9.5)
        run.font.bold = False
        run.font.color.rgb = BODY
        p.space_after = Pt(6)
        
    p = tf15_r.add_paragraph()
    p.text = "────────────────────────────────────────────────"
    p.font.name = 'Calibri'
    p.font.size = Pt(8.5)
    p.font.color.rgb = BLUE_BORDER
    p.space_after = Pt(6)
    
    p = tf15_r.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "We look forward to your questions and the Round 3 demonstration!"
    p.font.name = 'Calibri'
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ORANGE

    # Save to docs/Saarthi_Round2_Deck.pptx
    output_path = 'docs/Saarthi_Round2_Deck.pptx'
    prs.save(output_path)
    print(f"Presentation successfully created with {len(prs.slides)} slides at {output_path}")

if __name__ == '__main__':
    create_presentation()
