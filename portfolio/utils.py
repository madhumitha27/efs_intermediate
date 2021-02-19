from io import StringIO
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa
import io as StringIO

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.replace(u'\ufeff', '').encode("latin-1")), result)
    if not pdf.err:
        return result.getvalue()
    return None