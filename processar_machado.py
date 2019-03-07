#!/usr/bin/env python3
'''
Script responsável pela criação dos arquivos `txt` e do sumário das obras
`obras_machado_de_assis.csv`.

Copyright (C) 2019 Luiz Eduardo Amaral <luizamaral306@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import os
import re

import pandas as pd
import PyPDF2
import textract

pd.options.display.max_colwidth = 139
pd.options.display.max_rows = 120

def main():
    df = pd.DataFrame()
    for (dirpath, dirnames, filenames) in os.walk("./pdf"):
        df_categoria = pd.DataFrame(filenames, columns=["arquivo"])
        df_categoria["caminho completo"] = dirpath+"/"+df_categoria["arquivo"]
        df_categoria["categoria"] = dirpath
        df_categoria["categoria"] = df_categoria["categoria"].str.replace("\.\/pdf\/", "")
        df = df.append(df_categoria)
    df = df.reset_index(drop=True)
    df["autor"] = "Machado de Assis"
    df["paginas"] = df["caminho completo"].apply(lambda row: PyPDF2.PdfFileReader(row).numPages)
    df["texto"] = df["caminho completo"].apply(lambda row: textract.process(row).decode("utf-8"))

    df["texto"] = df["texto"].str.replace("\[[^]]+\]", "")  # Remoção das marcações das notas de rodapé

    df["cabecalho"] = df["texto"].str.slice(0, 1000)
    df["titulo"] = df["cabecalho"].str.replace("(?si)(.*?)(Textos?-Fonte|(Texto de|Edição) referência).*", "\\1")
    df["edicao"] = df[["titulo", "cabecalho"]].apply(lambda row: row["cabecalho"][len(row["titulo"]):], axis=1)
    df["edicao"] = df["edicao"].str.replace("(?si)(.*?)(Publicad[oa]|Introdução|Resposta|Carta|Discursos|Índice).*", "\\1")
    df["publicacao"] = df[["titulo", "edicao", "cabecalho"]].apply(lambda row: row["cabecalho"][len(row["titulo"])+len(row["edicao"]):], axis=1)
    df["publicacao"] = df["publicacao"].str.replace("(?si)(.*?)(\n\n|ÍNDICE).*", "\\1")

    df["texto"] = df[["texto", "titulo", "edicao", "publicacao"]].apply(lambda row: row["texto"][len(row["titulo"])+len(row["edicao"])+len(row["publicacao"]):], axis=1)

    df["titulo"] = df["titulo"].str.strip().str.replace("\n+", " ")
    df["edicao"] = df["edicao"].str.strip().str.replace("\n+", " ")
    df["publicacao"] = df["publicacao"].str.strip().str.replace("\n+", " ")

    df["publicacao ano"] = df["publicacao"].str.extract(".*(\d{4})").fillna(0).astype(int)
    publicacao_editora = [
        "Diário do Rio de Janeiro",
        "Gazeta de Notícias",
        "O Comércio de São Paulo",
        "Semana Literaria",
        "A Marmota",
        "Revista Brasileira",
        "O Cruzeiro",
        "Correio Mercantil",
        "Revista do Brasil",
        "Editora Garnier",
        "O Novo Mundo",
        "W. M. Jackson",
        "Tipografia Perseverança",
        "Laemmert & C. Editores",
        "Lombaerts & Cia",
        "Tipografia do Diário do RJ",
        "Tipografia do Imperial Instituto Artístico",
        "Semana Ilustrada",
        "Jornal do Comércio",
        "Tipografia Moreira",
        "A Ilustração",
        "O Espelho",
        "Jornal do Povo",
        "Imprensa Acadêmica",
        "O Globo",
        "A Estação",
        "B.-L. Garnier",
        "Gazeta de Noticias",
        "Outras Relíquias",
        "Poesias Completas",
        "O Futuro",
        "Revista Literária",
        "Ilustração Brasileira",
        "O Álbum",
        "A Crença",
        "Paula Brito",
        "Jornal da Tarde"
    ]
    df["publicacao editora"] = df["publicacao"].str.extract("(?i)({0})".format("|".join(publicacao_editora))).fillna("")
    cidades = [
        "Rio de Janeiro",
        "São Paulo",
    ]
    cidades_revistas_rj = [
        "O Cruzeiro",
        "O Globo",
        "A Estação",
        "Revista Brasileira",
        "Jornal do Comércio",
        "Gazeta de Notícias"
    ]
    cidades_revistas_sp = [
        "Revista do Brasil"
    ]
    df["publicacao cidade"] = df["publicacao"].str.extract("(?i)({0})".format("|".join(cidades+cidades_revistas_rj+cidades_revistas_sp))).fillna("")
    df["publicacao cidade"] = df["publicacao cidade"].str.replace("|".join(cidades_revistas_rj), "Rio de Janeiro")
    df["publicacao cidade"] = df["publicacao cidade"].str.replace("|".join(cidades_revistas_sp), "São Paulo")

    df["edicao ano"] = df["edicao"].str.extract(".*(\d{4})").fillna(0).astype(int)
    edicao_editora = [
        "W. ?M. Jackson",
        "Nova Aguilar",
        "Martins Fontes",
        "Edições Jackson",
        "Editora Nova Cultural",
        "Hedra"
    ]
    df["edicao editora"] = df["edicao"].str.extract("(?i)({0})".format("|".join(edicao_editora))).fillna("")
    df["edicao editora"] = df["edicao editora"].str.replace("W. ?M. Jackson", "W. M. Jackson",)

    df["edicao cidade"] = df["edicao"].str.extract("(?i)({0}|W.M. Jackson)".format("|".join(cidades))).fillna("")
    df["edicao cidade"] = df["edicao cidade"].str.replace("W.M. Jackson", "Rio de Janeiro")

    edicao_titulo = [
        "Obra Completa, de Machado de Assis",
        "Obras? Completas? de Machado de Assis",
        "Obra Completa, Machado de Assis",
        "Teatro de Machado de Assis",
        "Os Trabalhadores do Mar",
        "Oliver Twist",
        "Poesias Completas, Machado de Assis",
        "Crítica Teatral",
        "Teatro, Machado de Assis",
        "Crítica Literária de Machado de Assis"
    ]
    df["edicao titulo"] = df["edicao"].str.extract("(?i)({0})".format("|".join(edicao_titulo))).fillna("")
    df["edicao volume"] = df["edicao"].str.extract("(?i)V[o]?[l]?[.]?[ ]?(I|II|III|IV|V),").fillna("")

    df["texto"] = df["texto"].str.replace("[\v\t\f]+", "").str.replace("[\n]{2,}", "\n")

    colunas = df.columns.tolist()
    colunas.remove("texto")
    colunas.remove("cabecalho")
    colunas.append("texto")
    df = df[colunas]
    df["texto"] = df["titulo"] + "\n" + df["texto"]


    df.to_csv("./obras_machado_de_assis.csv", index=False)

    df["caminho completo txt"] = df["caminho completo"].str.replace("/pdf/", "/txt/").str.replace("\.pdf$", ".txt")

    def salvar_texto(linha):
        with open(linha["caminho completo txt"], "w") as fp:
            fp.write(linha["texto"])
    df.apply(salvar_texto, axis=1)


if __name__ == '__main__':
    main()
