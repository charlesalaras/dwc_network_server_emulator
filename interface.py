from textual.app import App, ComposeResult
from textual.containers import Center, ScrollableContainer, Horizontal, Middle, Vertical, Grid
from textual.screen import Screen, ModalScreen
from textual.widgets import Button, Label, Header, Footer, Static, TabbedContent, TabPane, Input, Pretty, SelectionList, RichLog
from textual.widgets.selection_list import Selection

class AdminScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
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
        yield Horizontal(
            RichLog(id="log"),
            SelectionList[int](
                Selection("Critical Level", 50),
                Selection("Error Level", 40),
                Selection("Warning Level", 30),
                Selection("Info Level", 20),
                Selection("Debug Level", 10),
                id="log-filter",
            ),
        )
    def on_mount(self):
        logger = self.query_one("#log", RichLog)
        logger.border_title = "Server Logs"
        filter = self.query_one("#log-filter", SelectionList)
        filter.border_title = "Log Filters"
class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Vertical(
            Horizontal(
                Label("Username"),
                Input(placeholder="Username", type="text", id="username", max_length=32)
            ),
            Horizontal(
                Label("Password"),
                Input(placeholder="Password", type="text", password=True, id="password", max_length=32)
            ),
            Center(Button("Login", variant="primary", id="submit")),
            id="login",
        )
    def on_button_pressed(self, event: Button.Pressed):
        username = self.query_one('#username', Input).value
        password = self.query_one('#password', Input).value
        if username == "admin" and password == "pass":
            self.query_one('#username', Input).value = ''
            self.query_one('#password', Input).value = ''
            self.app.push_screen(AdminScreen())
        else:
            self.query_one('#username', Input).value = ''
            self.query_one('#password', Input).value = ''

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
            self.app.pop_screen()
            self.app.pop_screen()
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
            # Kill the server here too
            self.app.exit()
        else:
            self.app.pop_screen()

class Interface(App):
    CSS_PATH = "interface.tcss"
    BINDINGS = [
        ('d', 'toggle_dark', 'Dark Mode'),
        ('l', 'logout', 'Log Out'),
        ('k', 'kill_server', 'Kill server')
    ]
    def on_mount(self):
        self.push_screen(LoginScreen())
    def action_toggle_dark(self):
        self.dark = not self.dark
    def action_logout(self):
        self.push_screen(LogoutModal())
    def action_kill_server(self):
        self.push_screen(WarningModal())
