class ScrollActionsMixin:
    def action_scroll_down(self):
        self.scroll_relative(y=5)

    def action_scroll_up(self):
        self.scroll_relative(y=-5)

    def action_scroll_home(self):
        self.scroll_home(animate=True)

    def action_scroll_end(self):
        self.scroll_end(animate=True)
