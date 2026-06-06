import asyncio
import os
import sys
import unittest
from string import Formatter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tg_msg_manager.i18n import DEFAULT_LANG, STRINGS, _, get_lang, set_lang, use_lang


def _format_placeholders(text: str) -> set[str]:
    placeholders: set[str] = set()
    for _literal, field_name, _format_spec, _conversion in Formatter().parse(text):
        if field_name:
            placeholders.add(field_name.split(".", 1)[0].split("[", 1)[0])
    return placeholders


class TestI18N(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        set_lang("ru")

    async def test_use_lang_restores_previous_language(self):
        set_lang("ru")

        with use_lang("en"):
            self.assertEqual(get_lang(), "en")
            self.assertEqual(_("menu_title"), "MAIN MENU")

        self.assertEqual(get_lang(), "ru")
        self.assertEqual(_("menu_title"), "ГЛАВНОЕ МЕНЮ")

    async def test_unknown_language_falls_back_to_default(self):
        set_lang("de")
        self.assertEqual(get_lang(), "ru")

        with use_lang("fr"):
            self.assertEqual(get_lang(), "ru")

    async def test_language_context_is_task_local(self):
        barrier = asyncio.Barrier(2)

        async def worker(lang: str) -> tuple[str, str]:
            with use_lang(lang):
                await barrier.wait()
                await asyncio.sleep(0)
                return get_lang(), _("menu_title")

        en_result, ru_result = await asyncio.gather(worker("en"), worker("ru"))

        self.assertEqual(en_result, ("en", "MAIN MENU"))
        self.assertEqual(ru_result, ("ru", "ГЛАВНОЕ МЕНЮ"))
        self.assertEqual(get_lang(), "ru")

    async def test_supported_locales_have_same_translation_keys(self):
        fallback_keys = set(STRINGS[DEFAULT_LANG])

        for lang, translations in STRINGS.items():
            with self.subTest(lang=lang):
                self.assertEqual(set(translations), fallback_keys)

    async def test_supported_locales_keep_fallback_format_placeholders(self):
        fallback = STRINGS[DEFAULT_LANG]

        for lang, translations in STRINGS.items():
            for key, fallback_text in fallback.items():
                with self.subTest(lang=lang, key=key):
                    self.assertEqual(
                        _format_placeholders(translations[key]),
                        _format_placeholders(fallback_text),
                    )


if __name__ == "__main__":
    unittest.main()
