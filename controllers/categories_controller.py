class CategoriesController:
    def __init__(self, view):
        self.view = view
        self._connect_signals()

    def _connect_signals(self):
        self.view.add_btn.clicked.connect(self.handle_add)
        self.view.edit_btn.clicked.connect(self.handle_edit)
        self.view.delete_btn.clicked.connect(self.handle_delete)

    def handle_add(self):
        print("CategoriesController: Nút Thêm danh mục được nhấn")

    def handle_edit(self):
        if self.view.selected_card:
            cat_id = self.view.selected_card.cat_data.get('id')
            print(f"CategoriesController: Nút Sửa danh mục được nhấn cho ID: {cat_id}")
        else:
            print("CategoriesController: Nút Sửa danh mục được nhấn, nhưng chưa chọn danh mục nào")

    def handle_delete(self):
        if self.view.selected_card:
            cat_id = self.view.selected_card.cat_data.get('id')
            print(f"CategoriesController: Nút Xóa danh mục được nhấn cho ID: {cat_id}")
        else:
            print("CategoriesController: Nút Xóa danh mục được nhấn, nhưng chưa chọn danh mục nào")
