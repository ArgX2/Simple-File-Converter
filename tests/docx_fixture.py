import zipfile

NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
TYPES = '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
RELS = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'


def make_docx(path, text='Hello', body=None):
    from xml.sax.saxutils import escape
    body = body if body is not None else '<w:p><w:r><w:t>' + escape(text) + '</w:t></w:r></w:p>'
    with zipfile.ZipFile(path, 'w') as package:
        package.writestr('[Content_Types].xml', TYPES)
        package.writestr('_rels/.rels', RELS)
        package.writestr('word/document.xml', f'<w:document xmlns:w="{NS}"><w:body>{body}</w:body></w:document>')
    return path
