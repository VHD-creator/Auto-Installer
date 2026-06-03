class ManagementController:
    def __init__(self, view):
        self.view = view
        self._connect_signals()

    def _connect_signals(self):
        self.view.add_btn.clicked.connect(self.handle_add)
        self.view.delete_btn.clicked.connect(self.handle_delete)

    def handle_add(self):
        print("ManagementController: Nút Thêm ứng dụng được nhấn")

    def handle_delete(self):
        if self.view.selected_apps:
            apps = [card.app_name for card in self.view.selected_apps]
            print(f"ManagementController: Nút Xóa ứng dụng được nhấn cho các ứng dụng: {', '.join(apps)}")
        else:
            print("ManagementController: Nút Xóa ứng dụng được nhấn, nhưng chưa chọn ứng dụng nào")
