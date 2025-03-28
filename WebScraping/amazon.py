import requests
import json
from bs4 import BeautifulSoup

# URL da página de ofertas da Amazon
URL_BASE = 'https://www.amazon.com.br/gp/goldbox/?ie=UTF8&pd_rd_w=ISD3d&content-id=amzn1.sym.63138262-fdd0-4724-8add-e4e26915e872&pf_rd_p=63138262-fdd0-4724-8add-e4e26915e872&pf_rd_r=YAXBTBECNVB4GMTMBKTB&pd_rd_wg=M8OxE&pd_rd_r=c55d011b-0f61-4cd9-b2ec-2c31cf35890e&ref_=pd_gw_unk'

# Simula um navegador para evitar bloqueios
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def coletar_dados_amazon():
    """
    Função para coletar dados dos produtos no widget de ofertas da Amazon.
    """
    session = requests.Session()
    response = session.get(URL_BASE, headers=HEADERS)

    if response.status_code != 200:
        print(f"Erro {response.status_code} ao acessar a página. Verifique sua conexão.")
        return []

    site = BeautifulSoup(response.text, 'html.parser')

    # Encontra o widget principal
    widget_principal = site.find('div', class_='celwidget', attrs={'cel_widget_id': 'dossier-browse_brbks2025-test-cml00'})
    if not widget_principal:
        print("Widget principal não encontrado. Verifique a estrutura da página e o ID do widget.")
        return []

    # Encontra o carrossel dentro do widget
    carousel = widget_principal.find('ol', class_='a-carousel')
    if not carousel:
        print("Carrossel de produtos não encontrado dentro do widget. Verifique a estrutura.")
        return []

    # Encontra cada item (produto) no carrossel
    produtos_li = carousel.find_all('li', class_='a-carousel-card')

    if not produtos_li:
        print("Nenhum produto encontrado no carrossel. Verifique as classes CSS.")
        return []

    lista_produtos = []

    for item_li in produtos_li[:10]:  # Limita a 10 produtos
        try:
            card_produto = item_li.find('div', class_='a-cardui dcl-product')
            if not card_produto:
                continue

            link_elemento = card_produto.find('a', class_='a-link-normal dcl-product-link')
            link = 'https://www.amazon.com.br' + link_elemento['href'] if link_elemento and 'href' in link_elemento.attrs else "#"

            imagem_elemento = card_produto.find('img', class_='a-dynamic-image dcl-dynamic-image')
            imagem = imagem_elemento['src'] if imagem_elemento and 'src' in imagem_elemento.attrs else "Imagem não encontrada"

            titulo_elemento = card_produto.find('span', class_='dcl-truncate dcl-product-title')
            nome_elemento = titulo_elemento.find('span') if titulo_elemento else None
            nome = nome_elemento.text.strip() if nome_elemento else "Nome não encontrado"

            # A partir daqui, o código para extrair outras informações permanece o mesmo...
            preco_novo_elemento = card_produto.find('span', class_='a-price dcl-product-price-new')
            preco_atual_offscreen = preco_novo_elemento.find('span', class_='a-offscreen').text.strip() if preco_novo_elemento and preco_novo_elemento.find('span', class_='a-offscreen') else None
            preco_atual_simbolo = preco_novo_elemento.find('span', class_='a-price-symbol').text.strip() if preco_novo_elemento and preco_novo_elemento.find('span', class_='a-price-symbol') else ''
            preco_atual_inteiro = preco_novo_elemento.find('span', class_='a-price-whole').text.strip() if preco_novo_elemento and preco_novo_elemento.find('span', class_='a-price-whole') else ''
            preco_atual_decimal = preco_novo_elemento.find('span', class_='a-price-fraction').text.strip() if preco_novo_elemento and preco_novo_elemento.find('span', class_='a-price-fraction') else '00'
            preco_atual = f"{preco_atual_simbolo}{preco_atual_inteiro},{preco_atual_decimal}" if preco_atual_offscreen else "Preço não encontrado"

            preco_antigo_elemento = card_produto.find('span', class_='a-price a-text-price dcl-product-price-old')
            preco_anterior = preco_antigo_elemento.text.strip() if preco_antigo_elemento else "Não disponível"

            avaliacao_elemento = card_produto.find('span', class_='dcl-product-rating-value')
            avaliacao = avaliacao_elemento.text.strip() if avaliacao_elemento else "Sem avaliação"

            num_avaliacoes_elemento = card_produto.find('span', class_='dcl-product-rating-count')
            numero_avaliacoes = num_avaliacoes_elemento.text.strip() if num_avaliacoes_elemento else "0"

            desconto = "A verificar"
            if preco_atual_offscreen and preco_anterior != "Não disponível":
                try:
                    preco_atual_num = float(preco_atual_offscreen.replace('R$\xa0', '').replace(',', '.'))
                    preco_anterior_num = float(preco_anterior.replace('R$\xa0', '').replace(',', '.'))
                    if preco_anterior_num > 0:
                        desconto_percentual = round(((preco_anterior_num - preco_atual_num) / preco_anterior_num) * 100)
                        desconto = f"{desconto_percentual}%"
                except ValueError:
                    desconto = "Erro ao calcular"

            frete_elemento = card_produto.find('div', class_='udm-primary-delivery-message')
            frete = frete_elemento.text.strip() if frete_elemento else "Frete não especificado"

            lista_produtos.append({
                "nome": nome,
                "imagem": imagem,
                "link": link,
                "preco_atual": preco_atual,
                "preco_anterior": preco_anterior,
                "avaliacao": avaliacao,
                "numero_avaliacoes": numero_avaliacoes,
                "desconto": desconto,
                "frete": frete,
                # Outras informações podem ser adicionadas aqui
            })

        except AttributeError as e:
            print(f"Erro ao processar um produto: {e}")
            continue

    return lista_produtos

def salvar_json(dados, nome_arquivo="produtos_amazon_widget.json"):
    """
    Salva os dados extraídos em um arquivo JSON.
    """
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    print(f"Dados do widget da Amazon salvos com sucesso em {nome_arquivo}")

if __name__ == "__main__":
    produtos_amazon = coletar_dados_amazon()

    if produtos_amazon:
        salvar_json(produtos_amazon)
        # Podemos imprimir os nomes para verificar rapidamente
        for produto in produtos_amazon:
            print(f"Nome: {produto['nome']}")
    else:
        print("Nenhum produto do widget da Amazon encontrado.")