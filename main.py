import os
from datetime import datetime

import flet as ft

import CRUD

NAV_ROUTES = ["/posts", "/add", "/preview"]
TOGGLE_MIN_CHARS = 450

TABS = [
    ("Published", "publish", ft.icons.PUBLISH_ROUNDED),
    ("Drafts", "draft", ft.icons.DRAFTS_ROUNDED),
    ("Trashed", "thrash", ft.icons.DELETE_ROUNDED),
]

PRIMARY = "#4F46E5"
DARK = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
BG = "#F5F7FB"
CARD = "#FFFFFF"
CHIP_BG = "#EDE9FE"
CHIP_FG = "#5B21B6"
TAB_BG = "#EEF2FF"
GREEN = "#16A34A"
AMBER = "#D97706"
RED = "#DC2626"


def validate(title, content, category):
    errors = {}
    title = (title or "").strip()
    content = (content or "").strip()
    category = (category or "").strip()

    if not title:
        errors["title"] = "Title wajib diisi"
    elif len(title) < 20:
        errors["title"] = "Title minimal 20 karakter"

    if not content:
        errors["content"] = "Content wajib diisi"
    elif len(content) < 200:
        errors["content"] = "Content minimal 200 karakter"

    if not category:
        errors["category"] = "Category wajib diisi"
    elif len(category) < 3:
        errors["category"] = "Category minimal 3 karakter"

    return errors, {"title": title, "content": content, "category": category}


def chip(text, bg=CHIP_BG, fg=CHIP_FG):
    return ft.Container(
        content=ft.Text(text, size=12, weight=ft.FontWeight.BOLD, color=fg),
        bgcolor=bg,
        padding=ft.padding.symmetric(horizontal=12, vertical=5),
        border_radius=20,
    )


def card(content, pad=24):
    return ft.Container(
        content=content,
        padding=pad,
        border_radius=16,
        bgcolor=CARD,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, spread_radius=2, color="#12000000"),
    )


def empty_state(msg):
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.icons.INBOX_ROUNDED, size=64, color="#C7D2FE"),
                ft.Text(msg, size=15, color=MUTED),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        alignment=ft.alignment.center,
        padding=48,
    )


def page_title(text, subtitle=None):
    controls = [ft.Text(text, size=24, weight=ft.FontWeight.BOLD, color=DARK)]
    if subtitle:
        controls.append(ft.Text(subtitle, size=13, color=MUTED))
    return ft.Column(controls, spacing=4)


def main(page: ft.Page):
    page.title = "Igam Article"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = BG
    page.padding = 0
    page.theme = ft.Theme(color_scheme_seed=PRIMARY)

    try:
        page.window.width = 1150
        page.window.height = 780
        page.window.min_width = 920
        page.window.min_height = 620
    except Exception:
        pass

    state = {
        "route": os.environ.get("FLET_ROUTE", "/posts"),
        "tab": 0,
        "expanded": set(),
        "snack": None,
    }

    def snack(text, ok=True):
        old = state.get("snack")
        if old is not None:
            try:
                page.overlay.remove(old)
            except ValueError:
                pass
        bar = ft.SnackBar(
            content=ft.Text(text, weight=ft.FontWeight.BOLD),
            bgcolor=GREEN if ok else RED,
        )
        state["snack"] = bar
        page.overlay.append(bar)
        bar.open = True
        page.update()

    def navigate(route, tab=None):
        state["route"] = route
        if tab is not None:
            state["tab"] = tab
        render()

    def build_appbar(route):
        titles = {"/posts": "All Posts", "/add": "Add New", "/preview": "Preview Blog"}
        if route.startswith("/edit/"):
            leading = ft.IconButton(
                icon=ft.icons.ARROW_BACK_ROUNDED,
                icon_color="#FFFFFF",
                tooltip="Kembali",
                on_click=lambda e: navigate("/posts", tab=state["tab"]),
            )
        else:
            leading = ft.IconButton(
                icon=ft.icons.MENU_ROUNDED,
                icon_color="#FFFFFF",
                tooltip="Buka menu",
                on_click=lambda e: page.open(state["drawer"]),
            )
        return ft.AppBar(
            title=ft.Text(
                titles.get(route, "Edit Article"),
                size=20,
                weight=ft.FontWeight.BOLD,
                color="#FFFFFF",
            ),
            bgcolor=PRIMARY,
            elevation=2,
            automatically_imply_leading=False,
            leading=leading,
            center_title=False,
        )

    def route_index(route):
        if route == "/add":
            return 1
        if route == "/preview":
            return 2
        return 0

    def select_drawer(drawer):
        page.close(drawer)
        navigate(NAV_ROUTES[drawer.selected_index])

    def build_drawer():
        return ft.NavigationDrawer(
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.icons.ARTICLE_ROUNDED, size=40, color="#FFFFFF"),
                            ft.Text(
                                "Igam Article",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color="#FFFFFF",
                            ),
                            ft.Text("Kelola article kamu", size=12, color="#C7D2FE"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    padding=ft.padding.symmetric(vertical=28, horizontal=16),
                    bgcolor=PRIMARY,
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.icons.ARTICLE_ROUNDED, label="All Posts"
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.icons.NOTE_ADD_ROUNDED, label="Add New"
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.icons.VISIBILITY_ROUNDED, label="Preview"
                ),
            ],
            selected_index=0,
            on_change=lambda e: select_drawer(e.control),
            bgcolor="#FFFFFF",
            indicator_color="#E0E7FF",
        )

    state["drawer"] = build_drawer()
    page.drawer = state["drawer"]

    def error_box(msg):
        return card(
            ft.Row(
                [
                    ft.Icon(ft.icons.ERROR_ROUNDED, color=RED, size=28),
                    ft.Text(f"Terjadi kesalahan: {msg}", color=DARK, size=15),
                ],
                spacing=12,
            )
        )

    def posts_table(rows):
        data_rows = []
        for r in rows:
            data_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    r["title"],
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=DARK,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                width=380,
                            )
                        ),
                        ft.DataCell(chip(r["category"] or "-")),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.EDIT_ROUNDED,
                                        icon_color=PRIMARY,
                                        tooltip="Edit",
                                        on_click=lambda e, a=r: navigate(f"/edit/{a['id']}"),
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE_ROUNDED,
                                        icon_color=RED,
                                        tooltip="Trash",
                                        on_click=lambda e, a=r: move_to_trash(a),
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Title", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Category", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(label=ft.Text("Action", weight=ft.FontWeight.BOLD)),
            ],
            rows=data_rows,
            border=ft.border.all(1, BORDER),
            border_radius=12,
            heading_row_color=ft.colors.with_opacity(0.1, PRIMARY),
        )
        
        # INI KUNCINYA BIAR MUNCUL
        return ft.Column(
            [table],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
       # return ft.Row([table], scroll=ft.ScrollMode.AUTO)

    def move_to_trash(article):
        try:
            CRUD.set_status(article["id"], "thrash")
        except Exception as ex:
            snack(f"Gagal memindahkan article: {ex}", ok=False)
            return
        judul = article["title"][:35] + ("..." if len(article["title"]) > 35 else "")
        snack(f'"{judul}" dipindahkan ke tab Trashed')
        state["tab"] = 2
        render()

    def set_tab(index):
        state["tab"] = index
        render()

    def view_posts():
        try:
            data = {status: CRUD.list_articles(status) for _, status, _ in TABS}
        except Exception as ex:
            return error_box(ex)

        tabs = []
        for index, (label, status, icon) in enumerate(TABS):
            rows = data[status]
            if rows:
                body = posts_table(rows)
            else:
                body = empty_state(f"Belum ada article pada tab {label}")
            tabs.append(
                ft.Tab(
                    tab_content=ft.Row(
                        [
                            ft.Icon(icon, size=18),
                            ft.Text(
                                f"{label} ({len(rows)})",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=6,
                    ),
                    content=ft.Container(body, padding=ft.padding.only(top=18)),
                )
            )

        return ft.Column(
            [
                page_title("All Posts", "Kelola article: publish, draft, maupun thrash"),
                ft.Tabs(
                    selected_index=state["tab"],
                    on_change=lambda e: set_tab(e.control.selected_index),
                    divider_color="#C7D2FE",
                    tabs=tabs,
                ),
            ],
            spacing=16,
        )

    def view_form():
        route = state["route"]
        article = None
        if route.startswith("/edit/"):
            try:
                article = CRUD.get_article(int(route.split("/")[2]))
            except Exception as ex:
                return error_box(ex)
            if article is None:
                return ft.Column(
                    [
                        empty_state("Article tidak ditemukan"),
                        ft.Row(
                            [
                                ft.FilledButton(
                                    text="Kembali ke All Posts",
                                    icon=ft.icons.ARROW_BACK_ROUNDED,
                                    on_click=lambda e: navigate("/posts"),
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=8,
                )

        f_title = ft.TextField(
            label="Title",
            value=article["title"] if article else "",
            helper_text="Wajib diisi, minimal 20 karakter",
            border_radius=10,
            filled=True,
        )
        f_content = ft.TextField(
            label="Content",
            value=article["content"] if article else "",
            helper_text="Wajib diisi, minimal 200 karakter",
            multiline=True,
            min_lines=6,
            max_lines=10,
            border_radius=10,
            filled=True,
        )
        f_category = ft.TextField(
            label="Category",
            value=article["category"] if article else "",
            helper_text="Wajib diisi, minimal 3 karakter",
            border_radius=10,
            filled=True,
        )

        def do_save(status_value):
            errors, cleaned = validate(
                f_title.value, f_content.value, f_category.value
            )
            f_title.error_text = errors.get("title")
            f_content.error_text = errors.get("content")
            f_category.error_text = errors.get("category")
            if errors:
                snack("Form belum memenuhi ketentuan validasi", ok=False)
                return

            payload = dict(cleaned, status=status_value)
            try:
                if article:
                    CRUD.update_article(article["id"], payload)
                    message = "Article berhasil diupdate"
                else:
                    CRUD.insert_article(payload)
                    message = "Article berhasil ditambahkan"
            except Exception as ex:
                snack(f"Gagal menyimpan: {ex}", ok=False)
                return

            snack(message)
            navigate("/posts", tab=0 if status_value == "publish" else 1)

        buttons = ft.Row(
            [
                ft.FilledButton(
                    text="Publish",
                    icon=ft.icons.UPLOAD_ROUNDED,
                    style=ft.ButtonStyle(
                        bgcolor=GREEN,
                        color="#FFFFFF",
                        padding=ft.padding.symmetric(horizontal=28, vertical=16),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    on_click=lambda e: do_save("publish"),
                ),
                ft.FilledButton(
                    text="Draft",
                    icon=ft.icons.SAVE_ROUNDED,
                    style=ft.ButtonStyle(
                        bgcolor=AMBER,
                        color="#FFFFFF",
                        padding=ft.padding.symmetric(horizontal=28, vertical=16),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    on_click=lambda e: do_save("draft"),
                ),
            ],
            spacing=12,
        )

        heading = page_title(
            f"Edit Article #{article['id']}" if article else "Add New Article",
            "Validasi: title min 20, content min 200, category min 3 karakter",
        )

        form = card(
            ft.Column(
                [heading, f_title, f_content, f_category, buttons],
                spacing=18,
            ),
            pad=28,
        )

        return ft.Row([form], alignment=ft.MainAxisAlignment.CENTER)

    def new_badge():
        return ft.Container(
            content=ft.Text("NEW", size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            bgcolor="#EF4444",
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            border_radius=8,
        )

    def category_header(category, count):
        return ft.Row(
            [
                ft.Row(
                    [
                        ft.Icon(ft.icons.FOLDER_ROUNDED, color=PRIMARY, size=22),
                        ft.Text(category, size=18, weight=ft.FontWeight.BOLD, color=DARK),
                        chip(f"{count} berita", bg=TAB_BG, fg=PRIMARY),
                    ],
                    spacing=8,
                ),
                ft.Row(
                    [
                        ft.Icon(ft.icons.SCHEDULE_ROUNDED, size=14, color=MUTED),
                        ft.Text("urut dari terbaru", size=12, color=MUTED),
                    ],
                    spacing=6,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def toggle_detail(article_id):
        if article_id in state["expanded"]:
            state["expanded"].discard(article_id)
        else:
            state["expanded"].add(article_id)
        render()

    def news_card(article, is_new=False):
        article_id = article["id"]
        content = article.get("content") or ""
        is_expanded = article_id in state["expanded"]
        updated = article.get("updated_date") or article.get("created_date")

        title_parts = []
        if is_new:
            title_parts.append(new_badge())
        title_parts.append(
            ft.Expanded(
                child=ft.Text(
                    article["title"],
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=DARK,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )
            )
        )
        title_parts.append(chip(article["category"] or "-"))

        controls = [
            ft.Row(
                title_parts,
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ]
        if updated:
            controls.append(
                ft.Row(
                    [
                        ft.Icon(ft.icons.SCHEDULE_ROUNDED, size=14, color=MUTED),
                        ft.Text(
                            f"Update {updated.strftime('%d %B %Y %H:%M')}",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                    spacing=6,
                )
            )
        controls.append(
            ft.Text(
                content,
                size=15,
                color="#374151",
                max_lines=None if is_expanded else 5,
                overflow=None if is_expanded else ft.TextOverflow.ELLIPSIS,
            )
        )
        if len(content) > TOGGLE_MIN_CHARS:
            controls.append(
                ft.TextButton(
                    text="sembunyikan" if is_expanded else "lihat semua",
                    icon=(
                        ft.icons.EXPAND_LESS_ROUNDED
                        if is_expanded
                        else ft.icons.EXPAND_MORE_ROUNDED
                    ),
                    style=ft.ButtonStyle(
                        color=PRIMARY,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    ),
                    on_click=lambda e, aid=article_id: toggle_detail(aid),
                )
            )
        return card(ft.Column(controls, spacing=10))

    def view_preview():
        try:
            rows = CRUD.list_articles("publish")
        except Exception as ex:
            return error_box(ex)

        controls = [
            page_title(
                "Preview Berita",
                "Article publish, dikelompokkan per category - terbaru di urutan atas",
            )
        ]

        if not rows:
            controls.append(empty_state("Belum ada article berstatus Publish"))
            return ft.Column(controls, spacing=16)

        rows = sorted(
            rows,
            key=lambda r: r.get("updated_date") or r.get("created_date") or datetime.min,
            reverse=True,
        )
        newest_id = rows[0]["id"]

        groups = {}
        for article in rows:
            groups.setdefault(article.get("category") or "Lainnya", []).append(article)

        for category, items in groups.items():
            controls.append(category_header(category, len(items)))
            for article in items:
                controls.append(news_card(article, is_new=article["id"] == newest_id))

        return ft.Column(controls, spacing=14)

    def render():
        route = state["route"]
        if route == "/add" or route.startswith("/edit/"):
            content = view_form()
        elif route == "/preview":
            content = view_preview()
        else:
            content = view_posts()

        page.appbar = build_appbar(route)
        state["drawer"].selected_index = route_index(route)
        page.drawer = state["drawer"]
        page.controls.clear()
        page.controls.append(
         #   ft.Column(
          #      [content],
           #     expand=True,
            #    scroll=ft.ScrollMode.AUTO,
             #   padding=ft.padding.symmetric(horizontal=28, vertical=20),
            #)
            ft.Container(
                content=ft.Column(
                    [content],
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.symmetric(horizontal=28, vertical=20),
                expand=True,)
        )
        page.update()

    render()


if __name__ == "__main__":
    import sys

    if "--web" in sys.argv:
        ft.app(
            target=main,
            view=ft.AppView.WEB_BROWSER,
            host="127.0.0.1",
            port=8550,
        )
    else:
        ft.app(target=main)
