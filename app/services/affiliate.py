import os

# --- Status da conta de afiliados (CJ Affiliate) ---
# Publisher ID (PID) confirmado: 8070424
# (o numero 7757355 que aparece nas URLs do painel e so um ID de sessao/membro
# da CJ, NAO e o PID - nao usar em links de afiliado)
#
# Candidaturas enviadas e pendentes de aprovacao (setembro/2026):
#   - Booking.com Brazil (advertiser 7854073)
#   - Expedia - Brazil (advertiser 5256787)
#   - trivago BR (advertiser 7819820)
#
# Enquanto pendente, a CJ nao permite gerar links de rastreamento funcionais.
# Quando aprovado, o formato a usar e o "Evergreen Link" da CJ (deep-link
# customizavel), que envolve a URL de destino com um redirecionamento da CJ
# (dominio + PID + ID do link) - formato exato ainda nao confirmado, pois so
# aparece ao gerar um link de verdade apos aprovacao. Assim que aprovado,
# gerar um link de exemplo no painel da CJ (Campanhas > Links e produtos >
# filtrar pelo advertiser > Evergreen Link) e atualizar esta funcao para
# montar esse formato em vez do simples "aid=" abaixo.
#
# Ate la, os links de pousada no seed funcionam normalmente como busca comum
# do Booking.com (sem comissao).


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
