"""
Extração de texto de arquivos enviados pelo Super-Admin (PDF/Word),
pra virar conteúdo de um DocumentoConhecimento sem precisar de
digitação manual.

pdfplumber pra PDF (extração de texto, não de tabelas — o conteúdo
vira texto corrido, igual aos documentos que já cadastramos manualmente
até aqui). python-docx pra Word (.docx apenas — .doc antigo não é
suportado por essa biblioteca, exigiria conversão à parte).
"""

import io

import pdfplumber
from docx import Document


class ExtracaoTextoError(Exception):
    """Erro ao extrair texto de um arquivo — mensagem já pronta pra mostrar ao usuário."""


def extrair_texto(nome_arquivo: str, conteudo_bytes: bytes) -> str:
    extensao = nome_arquivo.lower().rsplit(".", 1)[-1] if "." in nome_arquivo else ""

    if extensao == "pdf":
        return _extrair_de_pdf(conteudo_bytes)
    if extensao == "docx":
        return _extrair_de_docx(conteudo_bytes)

    raise ExtracaoTextoError(
        f"Formato '.{extensao}' não suportado. Envie um arquivo .pdf ou .docx "
        f"(.doc antigo do Word não é suportado — salve como .docx antes)."
    )


def _extrair_de_pdf(conteudo_bytes: bytes) -> str:
    try:
        partes = []
        with pdfplumber.open(io.BytesIO(conteudo_bytes)) as pdf:
            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    partes.append(texto_pagina)
    except Exception as erro:
        raise ExtracaoTextoError(f"Não foi possível ler o PDF: {erro}") from erro

    texto = "\n\n".join(partes).strip()
    if not texto:
        raise ExtracaoTextoError(
            "Não foi encontrado texto neste PDF — se for um documento "
            "escaneado (imagem), a extração automática de texto não "
            "funciona sem OCR, que ainda não está implementado aqui."
        )
    return texto


def _extrair_de_docx(conteudo_bytes: bytes) -> str:
    try:
        documento = Document(io.BytesIO(conteudo_bytes))
        partes = [p.text for p in documento.paragraphs if p.text.strip()]
    except Exception as erro:
        raise ExtracaoTextoError(f"Não foi possível ler o arquivo Word: {erro}") from erro

    texto = "\n\n".join(partes).strip()
    if not texto:
        raise ExtracaoTextoError("Não foi encontrado texto neste arquivo Word.")
    return texto
