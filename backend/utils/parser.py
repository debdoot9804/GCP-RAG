import tempfile
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.pptx import partition_pptx
from unstructured.partition.text import partition_text

def parse_file(filename: str, file_bytes: bytes) -> str:
    """Extract text content from supported files."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=filename) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    if filename.endswith(".pdf"):
        elements = partition_pdf(filename=tmp_path, strategy="hi_res")
    elif filename.endswith(".docx"):
        elements = partition_docx(filename=tmp_path)
    elif filename.endswith(".pptx"):
        elements = partition_pptx(filename=tmp_path)
    elif filename.endswith(".txt"):
        elements = partition_text(filename=tmp_path)
    else:
        raise ValueError(f"Unsupported file type: {filename}")

    return "\n".join([el.text for el in elements if hasattr(el, "text") and el.text])
