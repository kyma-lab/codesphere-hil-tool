class File:
    def __init__(self, title: str, content: str):
        self.title = str(title)
        self.content = str(content)

        if not self.title:
            raise ValueError("Title is empty")
        if not self.content:
            raise ValueError("Content is empty")

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = str(title)

    def get_content(self):
        return self.content

    def set_content(self, content):
        self.content = str(content)