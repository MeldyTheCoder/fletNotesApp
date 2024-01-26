import flet
import database


class App:
    def __init__(self, page: flet.Page):
        self.page = page

        self.themes = [
            flet.ThemeMode.LIGHT,
            flet.ThemeMode.DARK
        ]

        self.page.title = 'Заметки'
        self.page.theme_mode = self.themes[1]
        self.page.vertical_alignment = flet.MainAxisAlignment.CENTER
        self.main_menu()

    @property
    def theme(self):
        return self.page.theme_mode

    @theme.setter
    def theme(self, value):
        if value not in self.themes:
            return

        self.page.theme_mode = value
        self.page.update()

    def next_theme(self):
        theme = self.theme
        theme_index = self.themes.index(theme) - 1
        self.theme = self.themes[theme_index]

    @property
    def notes(self):
        return database.Note.fetch_all()

    def __delete_note(self, note):
        database.Note.delete(id=note.id)
        return self.main_menu()

    def __edit_note(self, note, **kwargs):
        database.Note.update(note.id, **kwargs)
        return self.main_menu()

    def _get_header(self, text):
        font_family = 'Cascadia Code'

        title = flet.Row(
            [
                flet.Icon(flet.icons.ARROW_RIGHT),
                flet.Text(text, size=26, font_family=font_family)
            ],
            alignment=flet.MainAxisAlignment.CENTER
        )

        theme_switch_callback = lambda *_: self.next_theme()

        return flet.AppBar(
            title=title,
            center_title=True,
            actions=[
                flet.IconButton(flet.icons.DARK_MODE, on_click=theme_switch_callback)
            ]
        )

    @staticmethod
    def _get_footer(*controls):
        return flet.BottomAppBar(
            content=flet.Row(
                [*controls],
                alignment=flet.MainAxisAlignment.CENTER
            )
        )

    @staticmethod
    def _get_body(*controls):
        return flet.Row(
            [
                flet.Column(
                    [*controls]
                )
            ],
            alignment=flet.MainAxisAlignment.CENTER
        )

    def edit_note_menu(self, note, **kwargs):
        self.page.clean()

        title = kwargs.get('title')
        text = kwargs.get('text')

        if title and text:
            return self.__edit_note(note, title=title, text=text)

        title_entry = flet.TextField(label='Заголовок заметки', value=note.title, width=1000)
        text_entry = flet.TextField(
            label='Текст заметки',
            value=note.text,
            multiline=True,
            shift_enter=True,
            width=1000
        )

        back_button_callback = lambda *_: self.main_menu()
        edit_button_callback = lambda *_: self.edit_note_menu(
            note,
            title=title_entry.value,
            text=text_entry.value
        )

        header = self._get_header(f'Редактирование заметки')

        body_container = self._get_body(
            title_entry,
            text_entry,
        )

        footer = self._get_footer(
            flet.OutlinedButton(
                text='Назад',
                icon=flet.icons.ARROW_BACK,
                on_click=back_button_callback
            ),
            flet.OutlinedButton(
                text='Редактировать',
                icon=flet.icons.EDIT,
                on_click=edit_button_callback
            )
        )

        self.page.add(
            header, body_container, footer
        )

    def _create_note_card(self, note):
        delete_callback = lambda *_: self.__delete_note(note)
        edit_callback = lambda *_: self.edit_note_menu(note)

        card = flet.Card(
            flet.ListTile(
                leading=flet.Icon(flet.icons.NOTE),
                title=flet.Text(note.title),
                subtitle=flet.Text(
                    note.text
                ),
                trailing=flet.PopupMenuButton(
                    icon=flet.icons.MORE_VERT,
                    items=[
                        flet.PopupMenuItem(text="Удалить", on_click=delete_callback),
                        flet.PopupMenuItem(text="Изменить", on_click=edit_callback),
                    ],
                ),
            )
        )

        return card

    def __create_note(self, title: str, text: str):
        database.Note.create(title=title, text=text)
        return self.main_menu()

    def note_card_creation_menu(self, **kwargs):
        self.page.clean()

        title = kwargs.get('title')
        text = kwargs.get('text')

        if title and text:
            return self.__create_note(title, text)

        title_entry = flet.TextField(
            label='Заголовок заметки',
            width=1000
        )

        text_entry = flet.TextField(
            label='Текст заметки',
            multiline=True,
            shift_enter=True,
            width=1000
        )

        add_button_callback = lambda *_: self.note_card_creation_menu(
            title=title_entry.value,
            text=text_entry.value
        )
        back_button_callback = lambda *_: self.main_menu()

        header = self._get_header('Создание заметки')
        body = self._get_body(
            title_entry,
            text_entry
        )
        footer = self._get_footer(
            flet.OutlinedButton(
                text='Назад',
                icon=flet.icons.ARROW_BACK,
                on_click=back_button_callback,
            ),
            flet.OutlinedButton(
                text='Создать заметку',
                icon=flet.icons.ADD,
                on_click=add_button_callback
            )
        )

        self.page.add(
            header, body, footer
        )

    def main_menu(self, **kwargs):
        self.page.clean()

        notes = self.notes
        button_callback = lambda *_: self.note_card_creation_menu()

        footer = self._get_footer(
            flet.OutlinedButton(
                text='Создать заметку',
                icon=flet.icons.ADD,
                on_click=button_callback
            )
        )

        header = self._get_header('Список Ваших Заметок')

        if notes:
            list_view = flet.ListView(auto_scroll=True, expand=1, height=400)

            for note in self.notes:
                list_view.controls.append(
                    self._create_note_card(note)
                )

            body_container = flet.Row(
                [
                    list_view
                ],
                alignment=flet.MainAxisAlignment.CENTER
            )

        else:
            body_container = self._get_body(
                flet.Text(value='Заметок пока нет :(', size=26, color=flet.colors.GREY)
            )

        self.page.add(
            header, body_container, footer
        )


flet.app(target=App)
