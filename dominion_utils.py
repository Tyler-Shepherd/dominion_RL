def buy_card(player, card, kingdom):
    if card.id != -1:
        assert kingdom[card.id] > 0
        player.discard.append(card)
        kingdom[card.id] -= 1