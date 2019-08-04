import dominion_utils

class Follow_Up:
    def __init__(self, type, person, props = None):
        self.gain_card_limit = None
        self.gainable_cards = []
        self.new_handsize = None

        self.type = type
        if type == 1:
            # Gain card up to
            self.gain_card_limit = props["gain_card_limit"]
            self.gainable_cards = dominion_utils.get_purchaseable_cards(self.gain_card_limit, person.kingdom)
            # todo add None option
        elif type == 2:
            # Discard down to
            self.new_handsize = props["handsize"]

    def serialize(self):
        return {
            "type": self.type,
            "gain_card_limit": self.gain_card_limit,
            "gainable_cards": dominion_utils.serialize_cards(self.gainable_cards),
            "new_handsize": self.new_handsize
        }