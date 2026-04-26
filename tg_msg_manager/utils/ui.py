import sys
import os
import platform
from typing import Any, Optional, Union
from datetime import datetime
from ..i18n import _

class UI:
    """
    Central utility for Terminal UI interactions, colors, and formatting.
    """
    # Unified 256-color palette for a cleaner CLI.
    CLR_TEXT = "\033[38;5;252m"
    CLR_MUTED = "\033[38;5;244m"
    CLR_BORDER = "\033[38;5;240m"
    CLR_ACCENT = "\033[38;5;81m"
    CLR_USER = "\033[38;5;222m"
    CLR_CHAT = "\033[38;5;117m"
    CLR_ID = "\033[38;5;110m"
    CLR_SUCCESS = "\033[38;5;114m"
    CLR_ERROR = "\033[38;5;203m"
    CLR_WARN = "\033[38;5;215m"
    CLR_STATS = "\033[38;5;150m"
    CLR_RESET = "\033[0m"
    CLR_BOLD = "\033[1m"
    CLR_CYAN = CLR_ACCENT

    STATUS_ICONS = {
        "Syncing": "◌",
        "Finished": "●",
        "Cleaning": "◌",
        "Found": "•",
        "Archiving": "◌",
        "Complete": "●",
    }

    SUMMARY_LABEL_KEYS = {
        "processed": "label_processed",
        "targets": "label_targets",
        "messages": "label_messages",
        "downloaded": "label_downloaded",
        "skipped": "label_skipped",
        "media": "label_media",
        "user_messages": "label_user_messages",
        "with_context": "label_with_context",
    }

    @staticmethod
    def is_tty() -> bool:
        return sys.stdout.isatty()

    @classmethod
    def paint(cls, text: Any, color: Optional[str] = None, bold: bool = False) -> str:
        rendered = str(text)
        if not cls.is_tty():
            return rendered
        prefix = ""
        if bold:
            prefix += cls.CLR_BOLD
        if color:
            prefix += color
        return f"{prefix}{rendered}{cls.CLR_RESET}"

    @classmethod
    def muted(cls, text: Any) -> str:
        return cls.paint(text, cls.CLR_MUTED)

    @classmethod
    def status_text(cls, label: str) -> str:
        key = f"status_{label.lower()}"
        translated = _(key)
        return translated if translated != key else label

    @classmethod
    def summary_label(cls, label: Any) -> str:
        key = cls.SUMMARY_LABEL_KEYS.get(str(label))
        if key:
            translated = _(key)
            if translated != key:
                return translated
        return str(label).replace("_", " ")

    @classmethod
    def rule(cls, width: int = 96) -> str:
        return cls.paint("─" * width, cls.CLR_BORDER)

    @classmethod
    def section(cls, title: str, icon: str = "•") -> str:
        return f"{cls.paint(icon, cls.CLR_ACCENT, bold=True)} {cls.paint(title, cls.CLR_TEXT, bold=True)}"

    @classmethod
    def key_value(cls, key: str, value: Any, icon: Optional[str] = None) -> str:
        parts = []
        if icon:
            parts.append(cls.paint(icon, cls.CLR_ACCENT))
        parts.append(cls.paint(key, cls.CLR_MUTED))
        parts.append(cls.paint(value, cls.CLR_STATS, bold=True))
        return " ".join(parts)

    @classmethod
    def format_name(cls, entity: Any, use_color: bool = False) -> str:
        """
        Standardizes how Telegram entities (Users/Chats) are displayed.
        """
        name = "Unknown"
        if hasattr(entity, 'first_name'):
            first = getattr(entity, 'first_name', '') or ''
            last = getattr(entity, 'last_name', '') or ''
            name = f"{first} {last}".strip()
            if not name:
                name = getattr(entity, 'username', '') or f"ID:{entity.id}"
        elif hasattr(entity, 'title'):
            name = getattr(entity, 'title', f"ID:{entity.id}")
        elif isinstance(entity, dict):
            # Handle dictionary representation from DB
            first = entity.get('first_name') or ''
            last = entity.get('last_name') or ''
            name = f"{first} {last}".strip() or entity.get('username') or f"ID:{entity.get('user_id', 'Unknown')}"
        elif isinstance(entity, (int, str)):
            name = f"ID:{entity}"

        if use_color:
            color = cls.CLR_USER if hasattr(entity, 'first_name') else cls.CLR_CHAT
            return cls.paint(name, color, bold=True)
        return name

    @classmethod
    def print_status(cls, label: str, value: Any, color: Optional[str] = None, extra: str = ""):
        """
        Prints a standardized status line: [Label] Value Extra
        Automatically handles TTY checks and line clearing.
        """
        if not cls.is_tty():
            return

        icon = cls.STATUS_ICONS.get(label, "•")
        label_text = cls.paint(cls.status_text(label), cls.CLR_TEXT, bold=True)
        icon_text = cls.paint(icon, color or cls.CLR_ACCENT, bold=True)
        value_text = cls.paint(value, color or cls.CLR_STATS, bold=True) if value not in ("", None) else ""
        extra_text = extra if extra else ""
        pieces = [piece for piece in (icon_text, label_text, value_text, extra_text) if piece]
        sys.stdout.write(f"\r   {'  '.join(pieces)}\033[K")
        sys.stdout.flush()

    @classmethod
    def print_header(cls, title: str, description: Optional[str] = None):
        """Prints a standardized submenu header."""
        cls.clear_screen()
        cls.print_gradient_banner()
        print(cls.rule(105))
        print(f" {cls.section(title, icon='◆')}")
        if description:
            print(f" {cls.muted(description)}")
        print(cls.rule(105))

    @staticmethod
    def clear_screen():
        """Clears the terminal screen."""
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    @classmethod
    def print_gradient_banner(cls):
        """Prints the ASCII banner with a vertical color gradient."""
        print() # Top margin
        banner = [
            "████████╗ ██████╗      ███╗   ███╗███████╗ ██████╗      ███╗   ███╗███╗   ██╗ ██████╗ ██████╗",
            "╚══██╔══╝██╔════╝      ████╗ ████║██╔════╝██╔════╝      ████╗ ████║████╗  ██║██╔════╝██╔══██╗",
            "   ██║   ██║  ███╗     ██╔████╔██║███████╗██║  ███╗     ██╔████╔██║██╔██╗ ██║██║  ███╗██████╔╝",
            "   ██║   ██║   ██║     ██║╚██╔╝██║╚════██║██║   ██║     ██║╚██╔╝██║██║╚██╗██║██║   ██║██╔══██╗",
            "   ██║   ╚██████╔╝     ██║ ╚═╝ ██║███████║╚██████╔╝     ██║ ╚═╝ ██║██║ ╚████║╚██████╔╝██║  ██║",
            "   ╚═╝    ╚═════╝      ╚═╝     ╚═╝╚══════╝ ╚═════╝      ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝",
        ]
        
        steps = len(banner)
        for i, line in enumerate(banner):
            r = int(0 + (255 - 0) * (i / (steps - 1)))
            g = int(255 + (0 - 255) * (i / (steps - 1)))
            b = 255
            # ANSI 24-bit color: \033[38;2;R;G;Bm
            # We add \r to ensure column 0
            sys.stdout.write(f"\r\033[38;2;{r};{g};{b}m{line}\033[0m\n")
        
        sys.stdout.write(f"\r\n{cls.paint('                     TG_MSG_MNGR by R.P.', cls.CLR_CYAN, bold=True)}\n")
        sys.stdout.flush()

    @classmethod
    def print_sync_summary(cls, stats: dict):
        """
        Prints the final summary of new messages found per user.
        Stats format: {user_id: {"name": str, "count": int}}
        """
        if not stats:
            return
        summaries = []
        for uid, info in stats.items():
            summaries.append({
                "title": info.get("name", f"ID:{uid}"),
                "lines": [("processed", info.get("count", 0))],
            })
        cls.print_final_summary("sync_summary_title", summaries)

    @classmethod
    def print_final_summary(cls, title_key: str, summaries: list[dict]):
        if not summaries:
            return

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print()
        print(cls.rule(72))
        print(f" {cls.section(_(title_key), icon='◆')}  {cls.muted(now_str)}")
        print(cls.rule(72))

        for item in summaries:
            print(f" {cls.paint(item.get('title', 'Summary'), cls.CLR_TEXT, bold=True)}")
            for label, value in item.get("lines", []):
                label_text = cls.paint(cls.summary_label(label), cls.CLR_MUTED)
                value_text = cls.paint(value, cls.CLR_STATS, bold=True)
                print(f"   {label_text}  {value_text}")
            print(cls.rule(72))
