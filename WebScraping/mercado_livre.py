import requests
import json
from bs4 import BeautifulSoup

# URL da página de ofertas do Mercado Livre
URL_BASE = 'https://www.mercadolivre.com.br/ofertas#nav-header'

# Simula um navegador para evitar bloqueios
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def coletar_dados():
    """
    Função para coletar dados dos produtos na página de ofertas do Mercado Livre.
    """
    session = requests.Session()
    response = session.get(URL_BASE, headers=HEADERS)

    if response.status_code != 200:
        print(f"Erro {response.status_code} ao acessar a página. Verifique sua conexão.")
        return []

    site = BeautifulSoup(response.text, 'html.parser')
    
    # Ajuste conforme a nova estrutura da página
    produtos = site.find_all('div', class_='andes-card')  # Ajuste essa classe conforme necessário

    if not produtos:
        print("Nenhum produto encontrado. Verifique se as classes CSS estão corretas.")
        return []

    lista_produtos = []

    for produto in produtos[:10]:  # Limita a 10 produtos para evitar sobrecarga
        try:
            nome = produto.find('a', class_='poly-component__title').text.strip()
            imagem = produto.find('img', class_='poly-component__picture')['src']
            link = produto.find('a', class_='poly-component__title')['href']
            
            preco_atual = produto.find('span', class_='andes-money-amount__fraction').text
            preco_centavos = produto.find('span', class_='andes-money-amount__cents')
            preco_atual = f"R$ {preco_atual},{preco_centavos.text if preco_centavos else '00'}"

            preco_anterior = produto.find('s', class_='andes-money-amount__fraction')
            preco_anterior = f"R$ {preco_anterior.text}" if preco_anterior else "Não disponível"

            desconto = produto.find('span', class_='andes-money-amount__discount')
            desconto = desconto.text if desconto else "Sem desconto"

            vendedor = produto.find('span', class_='poly-component__seller')
            vendedor = vendedor.text.strip() if vendedor else "Desconhecido"

            avaliacao = produto.find('span', class_='poly-reviews__rating')
            avaliacao = avaliacao.text.strip() if avaliacao else "Sem avaliação"

            num_avaliacoes = produto.find('span', class_='poly-reviews__total')
            num_avaliacoes = num_avaliacoes.text.strip() if num_avaliacoes else "0"

            parcelas = produto.find('span', class_='poly-price__installments')
            parcelas = parcelas.text.strip() if parcelas else "Sem parcelamento"

            frete = produto.find('div', class_='poly-component__shipping')
            frete = frete.text.strip() if frete else "Frete não especificado"

            lista_produtos.append({
                "nome": nome,
                "imagem": imagem,
                "preco_atual": preco_atual,
                "preco_anterior": preco_anterior,
                "desconto": desconto,
                "vendedor": vendedor,
                "avaliacao": avaliacao,
                "numero_avaliacoes": num_avaliacoes,
                "parcelas": parcelas,
                "frete": frete,
                "link": link
            })

        except AttributeError:
            continue  # Pula o produto caso falte algum dado essencial

    return lista_produtos

def salvar_json(dados, nome_arquivo="produtos_mercadolivre.json"):
    """
    Salva os dados extraídos em um arquivo JSON.
    """
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    print(f"Dados salvos com sucesso em {nome_arquivo}")

if __name__ == "__main__":
    produtos = coletar_dados()

    if produtos:
        salvar_json(produtos)
    else:
        print("Nenhum produto encontrado.")
