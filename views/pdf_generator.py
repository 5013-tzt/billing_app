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
        """Payment details ကို page အောက်ဆုံးမှာ canvas ဖြင့်ဆွဲမယ်"""
        payment = invoice_data.get('payment', {})
        has_payment = any([
            payment.get('bank_name'), payment.get('beneficiary'),
            payment.get('account_no'), payment.get('kpay_no'),
        ])
        if not has_payment:
            return

        canv.saveState()

        left_x   = 12 * mm
        right_x  = A4[0] - 12 * mm
        usable_w = right_x - left_x
        footer_h = 18 * mm
        bottom_y = 6 * mm
        line_y   = bottom_y + footer_h

        # separator line
        canv.setStrokeColor(colors.lightgrey)
        canv.setLineWidth(0.4)
        canv.line(left_x, line_y, right_x, line_y)

        # "PAYMENT DETAILS:" label
        label_y = line_y - 4 * mm
        canv.setFont('Helvetica-Bold', 7)
        canv.setFillColor(colors.grey)
        canv.drawString(left_x, label_y, "PAYMENT DETAILS:")

        # Row 1: Bank | Beneficiary
        row1_parts = []
        if payment.get('bank_name'):
            row1_parts.append(f"Bank: {payment['bank_name']}")
        if payment.get('beneficiary'):
            row1_parts.append(f"Beneficiary: {payment['beneficiary']}")

        # Row 2: Account No | KPay
        row2_parts = []
        if payment.get('account_no'):
            row2_parts.append(f"Account No: {payment['account_no']}")
        if payment.get('kpay_no'):
            row2_parts.append(f"KPay: {payment['kpay_no']}")

        col_w  = usable_w / 2
        row1_y = label_y - 4 * mm
        row2_y = row1_y  - 4 * mm

        canv.setFont('Helvetica', 7.5)
        canv.setFillColor(colors.black)
        for i, text in enumerate(row1_parts):
            canv.drawString(left_x + i * col_w, row1_y, text)
        for i, text in enumerate(row2_parts):
            canv.drawString(left_x + i * col_w, row2_y, text)

        canv.restoreState()

    def generate_invoice(self, invoice_data):
        """PDF ဖိုင်ထုတ်လုပ်ခြင်း"""
        self.doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            rightMargin=12*mm,
            leftMargin=12*mm,
            topMargin=8*mm,
            bottomMargin=28*mm        # footer နေရာအတွက် ချန်
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

        # Name — show_name toggle နှိပ်မှ contact_name ပေါ်မယ်
        # toggle မနှိပ်ရင် (contact_name=None) → "Valued Client" ပြမယ်
        if client.get('contact_name'):
            client_lines.append(Paragraph(client['contact_name'], self.styles['ClientName']))
        else:
            client_lines.append(Paragraph("Valued Client", self.styles['ClientName']))

        # Position — show_position toggle + data ၂ ခုလုံး လိုတယ်
        if client.get('contact_pos'):
            client_lines.append(Paragraph(client['contact_pos'], self.styles['NormalText']))

        # Phone — show_phone toggle + data ၂ ခုလုံး လိုတယ်
        if client.get('contact_ph'):
            client_lines.append(Paragraph(f"Tel: {client['contact_ph']}", self.styles['NormalText']))

        # Email — show_email toggle + data ၂ ခုလုံး လိုတယ်
        if client.get('contact_email'):
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