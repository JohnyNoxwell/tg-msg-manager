import sys
import os
import platform
from typing import Any, Optional, Union
from datetime import datetime

class UI:
    """
    Central utility for Terminal UI interactions, colors, and formatting.
    """
    # ANSI Colors (8-bit / 4-bit)
    CLR_USER = "\033[93m"    # Yellow
    CLR_CHAT = "\033[95m"    # Magenta
    CLR_ID = "\033[94m"      # Blue
    CLR_SUCCESS = "\033[92m" # Green
    CLR_ERROR = "\033[91m"   # Red
    CLR_WARN = "\033[93m"    # Yellow/Orange
    CLR_STATS = "\033[90m"   # Gray
    CLR_RESET = "\033[0m"
    CLR_BOLD = "\033[1m"
    CLR_CYAN = "\033[36m"

    @staticmethod
    def is_tty() -> bool:
        return sys.stdout.isatty()

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
            return f"{color}{name}{cls.CLR_RESET}"
        return name

    @classmethod
    def print_status(cls, label: str, value: Any, color: Optional[str] = None, extra: str = ""):
        """
        Prints a standardized status line: [Label] Value Extra
        Automatically handles TTY checks and line clearing.
        """
        if not cls.is_tty():
            return
            
        c = color or cls.CLR_SUCCESS
        # \r ensures we start at the beginning of the line
        # \033[K clears the rest of the line
        sys.stdout.write(f"\r   📊 [{cls.CLR_ID}{label}{cls.CLR_RESET}] {c}{value}{cls.CLR_RESET} {extra}\033[K")
        sys.stdout.flush()

    @classmethod
    def print_header(cls, title: str, description: Optional[str] = None):
        """Prints a standardized submenu header."""
        cls.clear_screen()
        cls.print_gradient_banner()
        print("=" * 105)
        print(f" 📂 {title}")
        print("=" * 105)
        if description:
            print(description)
            print("-" * 105)

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
        
        sys.stdout.write(f"\r\n{cls.CLR_CYAN}{cls.CLR_BOLD}                     TG_MSG_MNGR by R.P.{cls.CLR_RESET}\n")
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
        from ..i18n import _
        if not summaries:
            return

        is_tty = cls.is_tty()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c_title = cls.CLR_CYAN if is_tty else ""
        c_label = cls.CLR_USER if is_tty else ""
        c_value = cls.CLR_SUCCESS if is_tty else ""
        c_reset = cls.CLR_RESET if is_tty else ""

        print("\n" + "=" * 60)
        print(f" {c_title}📊 {_('sync_summary_title')}{c_reset} [{now_str}]")
        print("=" * 60)

        for item in summaries:
            print(f" {c_label}{item.get('title', 'Summary')}{c_reset}")
            for label, value in item.get("lines", []):
                print(f"   {label}: {c_value}{value}{c_reset}")
            print("-" * 60)

        print("=" * 60)
