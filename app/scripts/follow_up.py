class Follow_Up:
    def __init__(self, type, props = None):
        self.type = type
        if type == 1:
            # Gain card up to
            self.gain_card_limit = props["gain_card_limit"]