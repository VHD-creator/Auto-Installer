class SidebarController:
    def __init__(self, sidebar):
        self.sidebar = sidebar
        self._connect_signals()

    def _connect_signals(self):
        self.sidebar.homeButton.clicked.connect(self.handle_home)
        self.sidebar.manageAppsButton.clicked.connect(self.handle_manage_apps)
        self.sidebar.settingsButton.clicked.connect(self.handle_settings)
        self.sidebar.app_btn.clicked.connect(self.handle_manage_apps)
        self.sidebar.category_btn.clicked.connect(self.handle_categories)

    def handle_home(self):
        print("SidebarController: Điều hướng về Home")
        self.sidebar._on_menu_click(self.sidebar.homeButton, "main")

    def handle_manage_apps(self):
        print("SidebarController: Điều hướng về Manage Apps")
        # Handle both the main manage button and the submenu button
        btn = self.sidebar.sender() if self.sidebar.sender() else self.sidebar.manageAppsButton
        self.sidebar._on_menu_click(btn, "manage")

    def handle_categories(self):
        print("SidebarController: Điều hướng về Categories")
        self.sidebar._on_menu_click(self.sidebar.category_btn, "categories")

    def handle_settings(self):
        print("SidebarController: Điều hướng về Settings")
        self.sidebar._on_menu_click(self.sidebar.settingsButton, "settings")
