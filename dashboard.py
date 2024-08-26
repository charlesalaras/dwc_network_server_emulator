from textual.app import App, ComposeResult
from textual.containers import Center, ScrollableContainer, Grid
from textual.screen import Screen, ModalScreen
from textual.widgets import Button, Label, Header, Footer, Static, TabbedContent, TabPane, Input

class AdminPage(Static):
    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Dashboard"):
                yield Label("Dashboard")
            with TabPane("FC Bans"):
                yield Label("FC Bans")
            with TabPane("Game Whitelist"):
                yield Label("Games Whitelist")
            with TabPane("IP Bans"):
                yield Label("IP Bans")
            with TabPane("MAC Bans"):
                yield Label("MAC Bans")
            with TabPane("Registered Consoles"):
                yield Label("Registered Consoles")
            with TabPane("SN Bans"):
                yield Label("SN Bans")
            with TabPane("User List"):
                yield Label("User List")
            with TabPane("Server Logs"):
                yield Label("Server Logs")

class LoginModal(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Username"),
            Input(placeholder="Username", type="text", max_length=32),
            Label("Password"),
            Input(placeholder="Password", type="text", max_length=32),
            Button("Login", variant="primary", id="submit"),
            id="login",
        )
        def on_button_pressed(self, event: Button.Pressed):
            self.app.login()

class LogoutModal(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to logout?", id="question"),
            Button("Yes", variant="primary", id="yes"),
            Button("No", variant="error", id="no"),
            id="modal",
        )
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes":
            self.app.exit()
        else:
            self.app.pop_screen()

class WarningModal(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Label("WARNING: All components will be forcefully shut off and all clients will be disconnected. Are you certain you want to kill the server?", id="question"),
            Button("Shut Down", variant="error", id="yes"),
            Button("Cancel", variant="primary", id="no"),
            id="modal",
        )
        def on_button_pressed(self, event: Button.Pressed):
            if event.button.id == "yes":
                pass
            else:
                self.app.pop_screen()

class Dashboard(App):
    CSS_PATH = "dashboard.tcss"
    BINDINGS = [
        ('d', 'toggle_dark', 'Dark Mode'),
        ('l', 'logout', 'Log Out'),
        ('k', 'kill_server', 'Kill server')
    ]
    def compose(self) -> ComposeResult:
        #yield Header()
        #yield Footer()
        #yield AdminPage()
        yield LoginModal()
    def action_toggle_dark(self):
        self.dark = not self.dark
    def action_logout(self):
        self.push_screen(LogoutModal())
    def action_kill_server(self):
        self.push_screen(WarningModal())
    def login(self):
        self.app.pop_screen()
        self.mount(Header())
        self.mount(Footer())
        self.mount(AdminPage())
