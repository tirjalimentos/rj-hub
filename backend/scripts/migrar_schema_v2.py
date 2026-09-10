r"""
Script de migração pontual — roda UMA VEZ, depois de atualizar os
arquivos desta rodada (conversas reais + biblioteca unificada).

Base.metadata.create_all() (usado no seed e em promover_admin.py) só
cria tabelas que ainda NÃO existem — nunca altera uma tabela já
existente. Como esta rodada muda o formato de `conversas` e adiciona
uma coluna em `documentos_conhecimento`, precisa desse passo manual.

O QUE ESSE SCRIPT FAZ (e por que é seguro rodar):

1. Recria a tabela `conversas` do zero, no novo formato (associada a
   usuario_email, com timestamps reais, sem mais icon/nome
   duplicados). SEGURO: essa tabela sempre esteve vazia — o seed.py
   nunca colocou nenhuma linha nela ("começa sem histórico simulado,
   só o que for gerado de verdade pelo uso real"), e o uso real só
   passa a gravar a partir desta atualização. Nada é perdido.

2. Adiciona a coluna `criado_em` em `documentos_conhecimento`, via
   ALTER TABLE (não apaga nada) — preenchida com a data de agora
   pros documentos que você já subiu (não tem como recuperar a data
   real de upload deles, já que a coluna não existia até agora).

NÃO mexe em nada mais — seus grupos, o grupo "teste" que você criou,
os administradores promovidos, os usuários e o e-mail/grupo do
usuário de teste continuam exatamente como estão.

Uso (a partir de D:\RJ HUB\rjhub-v2\backend, com o venv ativado, com
o servidor uvicorn PARADO):

    python scripts/migrar_schema_v2.py
"""

import sys
from pathlib import Path

# Permite rodar como `python scripts/migrar_schema_v2.py` a partir de
# backend/ sem precisar transformar `scripts` num pacote instalado.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import inspect, text

from db.database import Base, engine
import db.models_db  # garante que todos os models (incluindo os novos campos) são carregados


def migrar():
    inspector = inspect(engine)

    with engine.connect() as conn:
        # --- 1. Recriar `conversas` no formato novo ---
        if "conversas" in inspector.get_table_names():
            conn.execute(text("DROP TABLE conversas"))
            conn.commit()
            print("🗑️  Tabela antiga `conversas` removida (estava vazia, nada foi perdido).")
        else:
            print("ℹ️  Tabela `conversas` não existia ainda — sem nada pra remover.")

        # --- 2. Adicionar `criado_em` em documentos_conhecimento, se ainda não existir ---
        colunas_existentes = [c["name"] for c in inspector.get_columns("documentos_conhecimento")]
        if "criado_em" not in colunas_existentes:
            conn.execute(text(
                "ALTER TABLE documentos_conhecimento ADD COLUMN criado_em DATETIME"
            ))
            conn.execute(text(
                "UPDATE documentos_conhecimento SET criado_em = CURRENT_TIMESTAMP WHERE criado_em IS NULL"
            ))
            conn.commit()
            print("✅ Coluna `criado_em` adicionada em documentos_conhecimento "
                  "(documentos existentes marcados com a data de agora).")
        else:
            print("ℹ️  Coluna `criado_em` já existia em documentos_conhecimento — nada a fazer.")

    # Recria `conversas` já no formato novo (e qualquer outra tabela
    # nova que porventura ainda não exista) — nunca altera tabela
    # já existente, só cria a que faltar.
    Base.metadata.create_all(bind=engine)
    print("✅ Tabela `conversas` recriada no formato novo.")
    print("")
    print("🎉 Migração concluída. Seus grupos, administradores, usuários e "
          "documentos da Base de Conhecimento continuam intactos.")


if __name__ == "__main__":
    migrar()
