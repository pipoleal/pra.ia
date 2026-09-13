import os


def link_com_afiliado(link: str | None) -> str | None:
    """Adiciona o ID de afiliado da Booking.com a um link, se configurado.

    Os links dos comercios sao salvos no banco sem o parametro `aid`. Assim,
    quando a variavel de ambiente BOOKING_AFFILIATE_ID for definida (ou
    trocada), toda a base de comercios/pousadas passa a gerar comissao
    imediatamente, sem precisar rodar o seed de novo ou alterar dados.
    """
    if not link or "booking.com" not in link or "aid=" in link:
        return link

    aid = os.getenv("BOOKING_AFFILIATE_ID")
    if not aid:
        return link

    separador = "&" if "?" in link else "?"
    return f"{link}{separador}aid={aid}"
