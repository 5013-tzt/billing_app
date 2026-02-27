import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas


class InvoicePDFGenerator:
    def __init__(self, filename=None):
        self.filename = filename or f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.elements = []
        self.doc = None

    def setup_custom_styles(self):
        """Premium စာသားပုံစံများသတ်မှတ်ခြင်း"""

        # INVOICE Title — ကြီးကြီး bold
        # parent မသုံး — Heading1 မှ hidden spaceBefore/After ကို ကာကွယ်ဖို့
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            fontSize=52,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            leading=56,             # fontSize နဲ့ ကိုက်ညီအောင်
            fontName='Helvetica-Bold'
        ))

        # မိခင်ကုမ္ပဏီအမည်
        self.styles.add(ParagraphStyle(
            name='MotherName',
            fontSize=14,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            leading=16,
            fontName='Helvetica-Bold'
        ))

        # Hotline / phone / email — gray
        self.styles.add(ParagraphStyle(
            name='Hotline',
            fontSize=9,
            textColor=colors.gray,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            leading=13,
            fontName='Helvetica'
        ))

        # Section Label (CLIENT DETAILS)
        self.styles.add(ParagraphStyle(
            name='SectionLabel',
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=1*mm,
            leading=10,
            fontName='Helvetica-Bold'
        ))

        # Client Name bold
        self.styles.add(ParagraphStyle(
            name='ClientName',
            fontSize=11,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=1*mm,
            fontName='Helvetica-Bold'
        ))

        # Normal Text gray
        self.styles.add(ParagraphStyle(
            name='NormalText',
            fontSize=9,
            textColor=colors.gray,
            alignment=TA_LEFT,
            leading=13,
            fontName='Helvetica'
        ))

        # Invoice Info Label — gray (INVOICE NO:, DATE OF ISSUE:, SERVICE TYPE: စာသားများ)
        self.styles.add(ParagraphStyle(
            name='InvoiceInfoLabel',
            fontSize=9,
            textColor=colors.gray,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))

        # Invoice Info Value — label gray, value normal black
        # "INVOICE NO:" gray bold + value bold black
        # "DATE OF ISSUE:" / "SERVICE TYPE:" gray + value normal black
        self.styles.add(ParagraphStyle(
            name='InvoiceInfoValue',
            fontSize=9,
            textColor=colors.gray,       # base gray; value ကို inline <font> tag သုံးပြီး black
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))

        # Invoice Number row style (INVOICE NO row)
        self.styles.add(ParagraphStyle(
            name='InvoiceNumber',
            fontSize=9,
            textColor=colors.gray,       # base gray; value ကို inline bold black
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))

        # Subject inline — "SUBJECT: Cleaning Service for January"
        self.styles.add(ParagraphStyle(
            name='SubjectInline',
            fontSize=9,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceBefore=2*mm,
            spaceAfter=1*mm,
            leading=12,
            fontName='Helvetica'
        ))

        # Table Header white text on black
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            fontSize=9,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Table Cell left
        self.styles.add(ParagraphStyle(
            name='TableCell',
            fontSize=9,
            textColor=colors.black,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))

        # Table Cell right-aligned
        self.styles.add(ParagraphStyle(
            name='TableCellRight',
            fontSize=9,
            textColor=colors.black,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))

        # ✅ FIX: Invoice Label for Receipt (gray, bold)
        self.styles.add(ParagraphStyle(
            name='InvoiceLabel',
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=2,
            leading=10,
            fontName='Helvetica-Bold'
        ))

        # ✅ FIX: Invoice Value for Receipt (black, normal)
        self.styles.add(ParagraphStyle(
            name='InvoiceValue',
            fontSize=9,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=4,
            leading=11,
            fontName='Helvetica'
        ))

        # Total Label light gray
        self.styles.add(ParagraphStyle(
            name='TotalLabelLight',
            fontSize=9,
            textColor=colors.gray,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))

        # Total Value light gray
        self.styles.add(ParagraphStyle(
            name='TotalValueLight',
            fontSize=9,
            textColor=colors.gray,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))

        # Grand Total Label bold black
        self.styles.add(ParagraphStyle(
            name='GrandTotalLabel',
            fontSize=10,
            textColor=colors.black,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))

        # Grand Total Amount big bold
        self.styles.add(ParagraphStyle(
            name='GrandTotalAmount',
            fontSize=14,
            textColor=colors.black,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))

        # Amount in Words Label
        self.styles.add(ParagraphStyle(
            name='AmountWordsLabel',
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_LEFT,
            spaceBefore=3*mm,
            spaceAfter=1*mm,
            fontName='Helvetica'
        ))

        # Amount in Words Value bold italic
        self.styles.add(ParagraphStyle(
            name='AmountWordsValue',
            fontSize=9,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=4*mm,
            fontName='Helvetica-BoldOblique'
        ))

        # Payment Details Header
        self.styles.add(ParagraphStyle(
            name='PaymentHeader',
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_RIGHT,
            spaceBefore=0,
            spaceAfter=1*mm,
            fontName='Helvetica-Bold'
        ))

        # Payment Details rows
        self.styles.add(ParagraphStyle(
            name='PaymentValue',
            fontSize=8,
            textColor=colors.black,
            alignment=TA_RIGHT,
            spaceBefore=0,
            spaceAfter=0,
            leading=12,
            fontName='Helvetica'
        ))

        # Footer center gray small
        self.styles.add(ParagraphStyle(
            name='Footer',
            fontSize=7,
            textColor=colors.lightgrey,
            alignment=TA_CENTER,
            spaceAfter=0,
            fontName='Helvetica'
        ))

    def add_watermark_logo(self, canv, doc, logo_path=None):
        """ရေစာ logo ထည့်ခြင်း — အလွန်ဖျော့"""
        if logo_path and os.path.exists(logo_path):
            try:
                canv.saveState()
                canv.setFillAlpha(0.04)
                img_width = A4[0] * 0.8
                img_height = A4[1] * 0.8
                canv.drawImage(
                    logo_path,
                    (A4[0] - img_width) / 2,
                    (A4[1] - img_height) / 2,
                    width=img_width, height=img_height,
                    preserveAspectRatio=True, mask='auto'
                )
                canv.restoreState()
            except Exception as e:
                pass

    def draw_payment_footer(self, canv, invoice_data):
        """
        Footer layout (ပုံပြထားတဲ့ design အတိုင်း):

        ─────────────────────────────────────────────────────────
        PAYMENT DETAILS:                          Thank You!
        Beneficiary: COMPANY NAME CO              Computer Generated Document
        KBZ Bank: 1234567890  |  KPay: 09xxxxxxx
        ─────────────────────────────────────────────────────────
        """
        payment = invoice_data.get('payment', {})
        mother  = invoice_data.get('mother_company', {})

        has_payment = any([
            payment.get('bank_name'), payment.get('beneficiary'),
            payment.get('account_no'), payment.get('kpay_no'),
        ])

        canv.saveState()

        page_w   = A4[0]
        left_x   = 12 * mm
        right_x  = page_w - 12 * mm
        usable_w = right_x - left_x
        footer_h = 22 * mm      # ပိုနေရာပေးမယ်
        bottom_y = 5 * mm
        line_y   = bottom_y + footer_h

        # ── Top separator line ─────────────────────────────────────────
        canv.setStrokeColor(colors.HexColor('#CCCCCC'))
        canv.setLineWidth(0.5)
        canv.line(left_x, line_y, right_x, line_y)

        # ── Right side: "Thank You!" + subtitle ───────────────────────
        thank_x = right_x
        thank_y = line_y - 5 * mm

        canv.setFont('Helvetica-Bold', 11)
        canv.setFillColor(colors.HexColor('#1A1A1A'))
        canv.drawRightString(thank_x, thank_y, "Thank You!")

        canv.setFont('Helvetica', 7.5)
        canv.setFillColor(colors.HexColor('#888888'))
        canv.drawRightString(thank_x, thank_y - 5 * mm, "Computer Generated Document")

        if not has_payment:
            canv.restoreState()
            return

        # ── Left side: PAYMENT DETAILS ────────────────────────────────
        cur_y = line_y - 4.5 * mm

        # "PAYMENT DETAILS:" label — gray small caps style
        canv.setFont('Helvetica-Bold', 7)
        canv.setFillColor(colors.HexColor('#888888'))
        canv.drawString(left_x, cur_y, "PAYMENT DETAILS:")
        cur_y -= 4.5 * mm

        # Beneficiary line
        if payment.get('beneficiary'):
            canv.setFont('Helvetica', 8)
            canv.setFillColor(colors.HexColor('#444444'))
            canv.drawString(left_x, cur_y, "Beneficiary: ")
            bene_x = left_x + canv.stringWidth("Beneficiary: ", 'Helvetica', 8)
            canv.setFont('Helvetica-Bold', 8)
            canv.setFillColor(colors.HexColor('#1A1A1A'))
            canv.drawString(bene_x, cur_y, payment['beneficiary'].upper())
            cur_y -= 4.5 * mm

        # Bank | KPay row  e.g.  KBZ Bank: 2750xxx  |  KPay: 09 447 902 411
        bank_parts = []
        if payment.get('bank_name') and payment.get('account_no'):
            bank_parts.append(
                (payment['bank_name'] + ": ", payment['account_no'])
            )
        elif payment.get('account_no'):
            bank_parts.append(("Account No: ", payment['account_no']))

        if payment.get('kpay_no'):
            bank_parts.append(("KPay: ", payment['kpay_no']))

        if bank_parts:
            cur_x = left_x
            for idx, (label, value) in enumerate(bank_parts):
                # separator pipe between items
                if idx > 0:
                    canv.setFont('Helvetica', 8)
                    canv.setFillColor(colors.HexColor('#AAAAAA'))
                    canv.drawString(cur_x, cur_y, "  |  ")
                    cur_x += canv.stringWidth("  |  ", 'Helvetica', 8)

                canv.setFont('Helvetica', 8)
                canv.setFillColor(colors.HexColor('#444444'))
                canv.drawString(cur_x, cur_y, label)
                cur_x += canv.stringWidth(label, 'Helvetica', 8)

                canv.setFont('Helvetica-Bold', 8)
                canv.setFillColor(colors.HexColor('#1A1A1A'))
                canv.drawString(cur_x, cur_y, value)
                cur_x += canv.stringWidth(value, 'Helvetica-Bold', 8)

        canv.restoreState()

    def generate_invoice(self, invoice_data):
        """PDF ဖိုင်ထုတ်လုပ်ခြင်း"""
        self.doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            rightMargin=12*mm,
            leftMargin=12*mm,
            topMargin=8*mm,
            bottomMargin=32*mm        # footer နေရာအတွက် ချန်
        )

        def on_page(canv, doc):
            self.add_watermark_logo(canv, doc, invoice_data.get('mother_company', {}).get('logo'))
            self.draw_payment_footer(canv, invoice_data)

        self.doc.build(self.elements, onFirstPage=on_page, onLaterPages=on_page)
        return self.filename

    def create_invoice(self, invoice_data):
        """Premium Invoice ဆောက်လုပ်ခြင်း"""
        self.elements = []
        page_width = A4[0] - 24*mm

        mother = invoice_data.get('mother_company', {})
        client = invoice_data.get('client', {})
        invoice_info = invoice_data.get('invoice', {})
        items = invoice_data.get('items', [])
        totals = invoice_data.get('totals', {})

        # ============================================================
        # === SECTION 1: Header Block — INVOICE ကြီး + Company Info ===
        # ============================================================
        # "INVOICE" title
        self.elements.append(Paragraph("INVOICE", self.styles['InvoiceTitle']))

        # INVOICE အောက် 2mm ခြား
        self.elements.append(Spacer(1, 2*mm))

        # Company name + Hotline + Email — ကျစ်ကျစ်လစ်လစ်
        if mother.get('name'):
            self.elements.append(Paragraph(mother['name'], self.styles['MotherName']))
        if mother.get('phone'):
            self.elements.append(Paragraph(f"Hotline: {mother['phone']}", self.styles['Hotline']))
        if mother.get('email'):
            self.elements.append(Paragraph(mother['email'], self.styles['Hotline']))

        # Separator — 2mm ပဲခြား
        self.elements.append(Spacer(1, 2*mm))
        self.elements.append(HRFlowable(
            width="100%", thickness=0.5, color=colors.lightgrey,
            spaceBefore=0, spaceAfter=2*mm
        ))

        # ============================================================
        # === SECTION 2: CLIENT DETAILS (left) + Invoice Info (right) ===
        # ============================================================

        # Left: client info lines
        client_lines = []

        if client.get('contact_name'):
            client_lines.append(Paragraph(client['contact_name'], self.styles['ClientName']))
        else:
            client_lines.append(Paragraph("Valued Client", self.styles['ClientName']))

        if client.get('show_position') and client.get('contact_pos'):
            client_lines.append(Paragraph(client['contact_pos'], self.styles['NormalText']))

        if client.get('show_phone') and client.get('contact_ph'):
            client_lines.append(Paragraph(f"Tel: {client['contact_ph']}", self.styles['NormalText']))

        if client.get('show_email') and client.get('contact_email'):
            client_lines.append(Paragraph(f"Email: {client['contact_email']}", self.styles['NormalText']))

        if client.get('company_name'):
            client_lines.append(Paragraph(client['company_name'], self.styles['ClientName']))

        if client.get('address'):
            client_lines.append(Paragraph(client['address'], self.styles['NormalText']))

        # Right: invoice info
        inv_no       = invoice_info.get('number', '')
        inv_date     = invoice_info.get('date', '')
        # database: invoices.service_type column တိုက်ရိုက်
        service_type = invoice_info.get('service_type', '')

        right_lines = [
            # "INVOICE NO:" gray + value bold black
            Paragraph(
                f'<font color="grey">INVOICE NO: </font>'
                f'<b><font color="black">{inv_no}</font></b>',
                self.styles['InvoiceNumber']
            ),
            # "DATE OF ISSUE:" gray + value normal black
            Paragraph(
                f'<font color="grey">DATE OF ISSUE: </font>'
                f'<font color="black">{inv_date}</font>',
                self.styles['InvoiceInfoValue']
            ),
            # "SERVICE TYPE:" gray + value normal black
            Paragraph(
                f'<font color="grey">SERVICE TYPE: </font>'
                f'<font color="black">{service_type}</font>',
                self.styles['InvoiceInfoValue']
            ),
        ]

        data = []
        data.append([
            Paragraph("CLIENT DETAILS:", self.styles['SectionLabel']),
            Paragraph("", self.styles['NormalText'])
        ])

        max_rows = max(len(client_lines), len(right_lines))
        for i in range(max_rows):
            left  = client_lines[i] if i < len(client_lines) else Paragraph("", self.styles['NormalText'])
            right = right_lines[i]  if i < len(right_lines)  else Paragraph("", self.styles['InvoiceInfoValue'])
            data.append([left, right])

        client_table = Table(data, colWidths=[page_width * 0.6, page_width * 0.4])
        client_table.setStyle(TableStyle([
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('ALIGN',         (0, 0), (0, -1),  'LEFT'),
            ('ALIGN',         (1, 0), (1, -1),  'RIGHT'),
            ('TOPPADDING',    (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('LEFTPADDING',   (0, 0), (-1, -1), 0),
            ('RIGHTPADDING',  (1, 0), (1, -1),  0),
        ]))
        self.elements.append(client_table)

        # ============================================================
        # === SECTION 3: SUBJECT inline (table အပေါ်တင်ကပ်)
        # ============================================================
        # SUBJECT — database: invoices.inv_title ကနေ ယူ
        # pass လုပ်ပုံ: invoice_info['inv_title'] = invoice_row['inv_title']
        subject_text = invoice_info.get('inv_title', '') or invoice_info.get('subject', '')
        if not subject_text and items:
            subject_text = items[0].get('description', '')

        if subject_text:
            self.elements.append(Paragraph(
                f'<font color="grey"><b>SUBJECT:</b></font> {subject_text}',
                self.styles['SubjectInline']
            ))
        else:
            self.elements.append(Spacer(1, 2*mm))

        # ============================================================
        # === SECTION 4: Items Table ===
        # ============================================================
        if items:
            table_data = [[
                Paragraph("DESCRIPTION", self.styles['TableHeader']),
                Paragraph("QTY",         self.styles['TableHeader']),
                Paragraph("UNIT PRICE",  self.styles['TableHeader']),
                Paragraph("AMOUNT",      self.styles['TableHeader'])
            ]]

            for item in items:
                table_data.append([
                    Paragraph(item.get('description', ''),         self.styles['TableCell']),
                    Paragraph(str(int(item.get('qty', 0))),        self.styles['TableCellRight']),
                    Paragraph(f"{item.get('unit_price', 0):,.0f}", self.styles['TableCellRight']),
                    Paragraph(f"{item.get('amount', 0):,.2f}",     self.styles['TableCellRight'])
                ])

            tbl = Table(
                table_data,
                colWidths=[page_width*0.45, page_width*0.15, page_width*0.2, page_width*0.2]
            )
            tbl.setStyle(TableStyle([
                # Header row
                ('BACKGROUND',    (0, 0), (-1, 0),  colors.black),
                ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
                ('ALIGN',         (0, 0), (-1, 0),  'CENTER'),
                ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
                ('FONTSIZE',      (0, 0), (-1, 0),  9),
                ('TOPPADDING',    (0, 0), (-1, 0),  7),
                ('BOTTOMPADDING', (0, 0), (-1, 0),  7),
                # Body rows
                ('BACKGROUND',    (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR',     (0, 1), (-1, -1), colors.black),
                ('ALIGN',         (0, 1), (0, -1),  'LEFT'),
                ('ALIGN',         (1, 1), (-1, -1), 'RIGHT'),
                ('FONTSIZE',      (0, 1), (-1, -1), 9),
                ('TOPPADDING',    (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                ('GRID',          (0, 0), (-1, -1), 0.4, colors.lightgrey),
            ]))

            self.elements.append(tbl)
            self.elements.append(Spacer(1, 4*mm))

        # ============================================================
        # === SECTION 5: Totals (right-aligned) ===
        # ============================================================
        totals_data = []

        totals_data.append([
            Paragraph("SUB TOTAL", self.styles['TotalLabelLight']),
            Paragraph(f"{totals.get('subtotal', 0):,.2f} MMK", self.styles['TotalValueLight'])
        ])

        if totals.get('tax', 0) > 0:
            totals_data.append([
                Paragraph("COMMERCIAL TAX (5%)", self.styles['TotalLabelLight']),
                Paragraph(f"{totals.get('tax', 0):,.2f} MMK", self.styles['TotalValueLight'])
            ])

        if totals.get('advance', 0) > 0:
            totals_data.append([
                Paragraph("ADVANCE", self.styles['TotalLabelLight']),
                Paragraph(f"-{totals.get('advance', 0):,.2f} MMK", self.styles['TotalValueLight'])
            ])

        totals_data.append([
            Paragraph("TOTAL AMOUNT", self.styles['GrandTotalLabel']),
            Paragraph(f"{totals.get('grand_total', 0):,.2f} MMK", self.styles['GrandTotalAmount'])
        ])

        totals_tbl = Table(totals_data, colWidths=[page_width * 0.7, page_width * 0.3])
        totals_tbl.setStyle(TableStyle([
            ('ALIGN',         (0, 0), (0, -1),  'RIGHT'),
            ('ALIGN',         (1, 0), (1, -1),  'RIGHT'),
            ('TOPPADDING',    (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            # Grand total top border
            ('LINEABOVE',     (0, -1), (-1, -1), 0.5, colors.lightgrey),
        ]))

        wrapper = Table([[totals_tbl]], colWidths=[page_width])
        wrapper.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'RIGHT')]))
        self.elements.append(wrapper)
        self.elements.append(Spacer(1, 4*mm))

        # ============================================================
        # === SECTION 6: Amount in Words ===
        # ============================================================
        # FIX: amount_in_words ကို generate_invoice ခေါ်ချိန်မှာ
        # number_to_words_mm(int(grand_total)) ဆိုပြီး pass လုပ်ပေးရမယ်
        amount_words = totals.get('amount_in_words', '')
        if not amount_words:
            # fallback: grand_total ကနေ auto-generate
            grand_total_val = totals.get('grand_total', 0)
            amount_words = number_to_words_mm(int(grand_total_val))

        self.elements.append(Paragraph("AMOUNT IN WORDS:", self.styles['AmountWordsLabel']))
        self.elements.append(Paragraph(amount_words, self.styles['AmountWordsValue']))
        self.elements.append(Spacer(1, 6*mm))


        return self.generate_invoice(invoice_data)


# ============================================================
# Number → English Words (MMK)
# ============================================================
    def create_receipt(self, invoice_data):
        """Payment Receipt PDF ဆောက်လုပ်ခြင်း — Paid invoice များအတွက်"""
        self.elements = []
        page_width = A4[0] - 24*mm

        mother  = invoice_data.get('mother_company', {})
        client  = invoice_data.get('client', {})
        inv     = invoice_data.get('invoice', {})
        totals  = invoice_data.get('totals', {})
        payment = invoice_data.get('payment', {})

        # ── Header ────────────────────────────────────────────────────
        self.elements.append(Paragraph("RECEIPT", self.styles['InvoiceTitle']))
        self.elements.append(Spacer(1, 2*mm))

        if mother.get('name'):
            self.elements.append(Paragraph(mother['name'], self.styles['MotherName']))
        if mother.get('phone'):
            self.elements.append(Paragraph(f"Hotline: {mother['phone']}", self.styles['Hotline']))
        if mother.get('email'):
            self.elements.append(Paragraph(mother['email'], self.styles['Hotline']))

        self.elements.append(Spacer(1, 2*mm))
        self.elements.append(HRFlowable(
            width="100%", thickness=0.5, color=colors.lightgrey,
            spaceBefore=0, spaceAfter=2*mm
        ))

        # ── Client + Receipt Info (2 columns) ─────────────────────────
        client_lines = []
        if client.get('contact_name'):
            client_lines.append(Paragraph(client['contact_name'], self.styles['ClientName']))
        else:
            client_lines.append(Paragraph("Valued Client", self.styles['ClientName']))
        if client.get('contact_pos'):
            client_lines.append(Paragraph(client['contact_pos'], self.styles['NormalText']))
        if client.get('contact_ph'):
            client_lines.append(Paragraph(f"Tel: {client['contact_ph']}", self.styles['NormalText']))
        if client.get('company_name'):
            client_lines.append(Paragraph(client['company_name'], self.styles['ClientName']))
        if client.get('address'):
            client_lines.append(Paragraph(client['address'], self.styles['NormalText']))

        paid_date = inv.get('paid_date') or datetime.now().strftime('%Y-%m-%d')
        receipt_lines = [
            Paragraph("RECEIPT NO", self.styles['InvoiceLabel']),
            Paragraph(f"REC-{inv.get('number','')}", self.styles['InvoiceValue']),
            Paragraph("INVOICE REF", self.styles['InvoiceLabel']),
            Paragraph(inv.get('number', ''), self.styles['InvoiceValue']),
            Paragraph("INVOICE DATE", self.styles['InvoiceLabel']),
            Paragraph(inv.get('date', ''), self.styles['InvoiceValue']),
            Paragraph("PAID DATE", self.styles['InvoiceLabel']),
            Paragraph(paid_date, self.styles['InvoiceValue']),
            Paragraph("SERVICE", self.styles['InvoiceLabel']),
            Paragraph(inv.get('service_type', ''), self.styles['InvoiceValue']),
        ]

        col_half = page_width / 2
        info_table = Table(
            [[client_lines, receipt_lines]],
            colWidths=[col_half, col_half]
        )
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        self.elements.append(info_table)
        self.elements.append(Spacer(1, 5*mm))
        self.elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey,
                                         spaceBefore=0, spaceAfter=3*mm))

        # ── PAID STAMP box ────────────────────────────────────────────
        stamp_style = ParagraphStyle(
            'PaidStamp', fontSize=28, fontName='Helvetica-Bold',
            textColor=colors.white, alignment=TA_CENTER, leading=32
        )
        stamp_table = Table(
            [[Paragraph("RECEIVED WITH THANKS", stamp_style)]],
            colWidths=[page_width]
        )
        stamp_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#16a34a')),
            ('ROUNDEDCORNERS', [6]),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        self.elements.append(stamp_table)
        self.elements.append(Spacer(1, 5*mm))

        # ── Amount Summary ────────────────────────────────────────────
        grand_total = totals.get('grand_total', 0)
        subtotal    = totals.get('subtotal', 0)
        tax         = totals.get('tax', 0)
        advance     = totals.get('advance', 0)
        amount_words = totals.get('amount_in_words', '')

        summary_data = [
            ["Description", "Amount (MMK)"],
        ]
        if subtotal:
            summary_data.append(["Subtotal", f"{subtotal:,.0f}"])
        if tax:
            summary_data.append(["Commercial Tax (5%)", f"{tax:,.0f}"])
        if advance:
            summary_data.append([f"Deduction / Advance", f"- {advance:,.0f}"])
        summary_data.append(["TOTAL RECEIVED", f"{grand_total:,.0f}"])

        col_desc  = page_width * 0.65
        col_amt   = page_width * 0.35
        sum_table = Table(summary_data, colWidths=[col_desc, col_amt])

        n = len(summary_data)
        sum_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
            ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0,0), (-1,0), 10),
            ('ALIGN',         (1,0), (1,0), 'RIGHT'),
            # Body
            ('FONTSIZE',      (0,1), (-1,-2), 10),
            ('ALIGN',         (1,1), (1,-1), 'RIGHT'),
            ('ROWBACKGROUNDS',(0,1), (-1,-2), [colors.white, colors.HexColor('#f8fafc')]),
            # Total row
            ('BACKGROUND',    (0,n-1), (-1,n-1), colors.HexColor('#16a34a')),
            ('TEXTCOLOR',     (0,n-1), (-1,n-1), colors.white),
            ('FONTNAME',      (0,n-1), (-1,n-1), 'Helvetica-Bold'),
            ('FONTSIZE',      (0,n-1), (-1,n-1), 12),
            # Grid
            ('GRID',          (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ]))
        self.elements.append(sum_table)
        self.elements.append(Spacer(1, 4*mm))

        # Amount in words
        if amount_words:
            words_style = ParagraphStyle(
                'AmtWords', fontSize=9, fontName='Helvetica-Oblique',
                textColor=colors.HexColor('#475569'), alignment=TA_LEFT
            )
            self.elements.append(
                Paragraph(f"Amount in words: {amount_words}", words_style)
            )

        self.elements.append(Spacer(1, 8*mm))
        self.elements.append(HRFlowable(width="100%", thickness=0.5,
                                         color=colors.lightgrey,
                                         spaceBefore=0, spaceAfter=2*mm))

        # ── Signature line ────────────────────────────────────────────
        sig_style = ParagraphStyle(
            'Sig', fontSize=9, fontName='Helvetica',
            textColor=colors.HexColor('#475569'), alignment=TA_CENTER
        )
        sig_table = Table(
            [[Paragraph("_______________________", sig_style),
              Paragraph("_______________________", sig_style)]],
            colWidths=[page_width/2, page_width/2]
        )
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        self.elements.append(sig_table)

        lbl_table = Table(
            [[Paragraph("Authorized Signature", sig_style),
              Paragraph("Received By", sig_style)]],
            colWidths=[page_width/2, page_width/2]
        )
        lbl_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        self.elements.append(lbl_table)

        # ── Build ─────────────────────────────────────────────────────
        return self.generate_invoice(invoice_data)


def number_to_words_mm(num):
    """
    ဂဏန်းကို English စကားလုံးပြောင်းခြင်း
    Usage (database ထဲကယူပြီး pass လုပ်ပုံ):
        amount_words = number_to_words_mm(int(invoice_row['grand_total']))
    """
    if not isinstance(num, (int, float)):
        return ''

    num = int(num)   # float ဆိုရင် int လုပ်

    units = ['', 'One', 'Two', 'Three', 'Four', 'Five',
             'Six', 'Seven', 'Eight', 'Nine']
    teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen',
             'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tens  = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty',
             'Sixty', 'Seventy', 'Eighty', 'Ninety']

    def convert_less_than_thousand(n):
        if n == 0:
            return ''
        elif n < 10:
            return units[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            return tens[n // 10] + (' ' + units[n % 10] if n % 10 != 0 else '')
        else:
            remainder = convert_less_than_thousand(n % 100)
            return units[n // 100] + ' Hundred' + (' ' + remainder if remainder else '')

    if num == 0:
        return 'Zero MMK Only.'

    result = []

    if num >= 1_000_000:
        result.append(convert_less_than_thousand(num // 1_000_000) + ' Million')
        num %= 1_000_000

    if num >= 1_000:
        result.append(convert_less_than_thousand(num // 1_000) + ' Thousand')
        num %= 1_000

    if num > 0:
        part = convert_less_than_thousand(num)
        if part:
            result.append(part)

    return ' '.join(result) + ' MMK Only.'