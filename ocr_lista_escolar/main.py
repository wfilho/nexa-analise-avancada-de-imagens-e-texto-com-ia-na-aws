# Importa os módulos necessários
import json  # Para manipular arquivos e dados no formato JSON
from pathlib import Path  # Para manipular caminhos de arquivos de forma cross-platform

import boto3  # SDK da AWS para interagir com os serviços, neste caso o Textract
from botocore.exceptions import ClientError  # Para capturar erros específicos do cliente AWS
from mypy_boto3_textract.type_defs import DetectDocumentTextResponseTypeDef  # Tipagem do Textract para melhorar a legibilidade

# Função para detectar texto em um arquivo de imagem
def detect_file_text() -> None:
    # Cria um cliente Textract para se comunicar com o serviço AWS
    client = boto3.client("textract")

    # Define o caminho do arquivo que será processado
    file_path = str(Path(__file__).parent / "images" / "lista-material-escolar.jpeg")
    
    # Lê o arquivo de imagem em formato binário
    with open(file_path, "rb") as f:
        document_bytes = f.read()

    try:
        # Envia o arquivo para o Textract e obtém a resposta
        response = client.detect_document_text(Document={"Bytes": document_bytes})
        
        # Escreve a resposta do Textract em um arquivo JSON para análise posterior
        with open("response.json", "w") as response_file:
            response_file.write(json.dumps(response))
    except ClientError as e:  # Captura possíveis erros na comunicação com o Textract
        print(f"Erro processando documento: {e}")

# Função para extrair todas as linhas de texto do arquivo JSON gerado
def get_lines() -> list[str]:
    try:
        # Abre e lê o arquivo JSON gerado pelo Textract
        with open("response.json", "r") as f:
            # Converte o conteúdo JSON em um dicionário Python
            data: DetectDocumentTextResponseTypeDef = json.loads(f.read())
            # Extrai a lista de blocos do documento processado
            blocks = data["Blocks"]
        
        # Retorna apenas os textos que foram classificados como linhas (LINE) pelo Textract
        return [block["Text"] for block in blocks if block["BlockType"] == "LINE"]  # type: ignore
    except IOError:  # Caso o arquivo JSON não exista, detecta o texto do documento original
        detect_file_text()
    return []

# Executa o script
if __name__ == "__main__":
    # Chama a função para extrair linhas de texto e as imprime uma por uma
    for line in get_lines():
        print(line)
