# Importa módulos necessários
from pathlib import Path
import boto3  # Biblioteca AWS SDK para Python
from mypy_boto3_rekognition.type_defs import (
    CelebrityTypeDef,
    RecognizeCelebritiesResponseTypeDef,
)  # Tipos de dados do serviço Rekognition
from PIL import Image, ImageDraw, ImageFont  # Manipulação de imagens

# Cria um cliente do serviço Rekognition da AWS
client = boto3.client("rekognition")


# Função para gerar o caminho do arquivo de imagem
def get_path(file_name: str) -> str:
    # Retorna o caminho completo da imagem na pasta 'images' relativa ao arquivo atual
    return str(Path(__file__).parent / "images" / file_name)


# Função que envia uma imagem para o Rekognition e reconhece celebridades
def recognize_celebrities(photo: str) -> RecognizeCelebritiesResponseTypeDef:
    with open(photo, "rb") as image:  # Abre a imagem no modo binário (rb)
        # Retorna a resposta do serviço Rekognition
        return client.recognize_celebrities(Image={"Bytes": image.read()})


# Função que desenha retângulos em torno das faces reconhecidas e salva o resultado
def draw_boxes(image_path: str, output_path: str, face_details: list[CelebrityTypeDef]):
    # Abre a imagem usando a biblioteca PIL
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)  # Permite desenhar sobre a imagem
    font = ImageFont.truetype("Ubuntu-R.ttf", 20)  # Define a fonte do texto

    width, height = image.size  # Obtém dimensões da imagem

    # Itera sobre os detalhes das faces reconhecidas
    for face in face_details:
        box = face["Face"]["BoundingBox"]  # Coordenadas do retângulo delimitador da face
        # Converte as coordenadas normalizadas (0-1) para pixels da imagem
        left = int(box["Left"] * width)
        top = int(box["Top"] * height)
        right = int((box["Left"] + box["Width"]) * width)
        bottom = int((box["Top"] + box["Height"]) * height)

        confidence = face.get("MatchConfidence", 0)  # Confiança de correspondência
        # Apenas desenha em faces com confiança superior a 90%
        if confidence > 90:
            # Desenha o retângulo em torno da face
            draw.rectangle([left, top, right, bottom], outline="red", width=3)

            # Obtém o nome da celebridade
            text = face.get("Name", "")
            position = (left, top - 20)  # Posição do texto acima do retângulo
            bbox = draw.textbbox(position, text, font=font)  # Define a área do texto
            draw.rectangle(bbox, fill="red")  # Fundo vermelho para o texto
            draw.text(position, text, font=font, fill="white")  # Texto em branco

    # Salva a imagem com as alterações no caminho especificado
    image.save(output_path)
    print(f"Imagem salva com resultados em : {output_path}")


# Bloco principal do script
if __name__ == "__main__":
    # Lista de imagens a serem processadas
    photo_paths = [
        get_path("bbc.jpg"),
        get_path("msn.jpg"),
        get_path("neymar-torcedores.jpg"),
    ]

    # Itera sobre cada imagem na lista
    for photo_path in photo_paths:
        # Chama a função para reconhecer celebridades
        response = recognize_celebrities(photo_path)
        faces = response["CelebrityFaces"]  # Obtém os detalhes das faces reconhecidas

        # Verifica se há celebridades detectadas
        if not faces:
            print(f"Não foram encontrados famosos para a imagem: {photo_path}")
            continue

        # Define o caminho de saída da imagem processada
        output_path = get_path(f"{Path(photo_path).stem}-resultado.jpg")
        # Desenha os retângulos e salva a imagem com resultados
        draw_boxes(photo_path, output_path, faces)
