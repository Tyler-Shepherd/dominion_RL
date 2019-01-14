import training.params as params

def buy_card(player, card, kingdom):
    if card.id != -1:
        kingdom.buy_card(card)
        player.discard.append(card)