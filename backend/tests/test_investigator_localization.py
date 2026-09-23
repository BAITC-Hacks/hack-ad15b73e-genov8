"""Offline checks: never call an external AI service."""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pydantic import ValidationError

from backend.app.agent.investigator import MoneyGraphInvestigator, SYSTEM_INSTRUCTIONS
from backend.app.agent.localization import CONTEXT, LANGUAGE_INSTRUCTIONS, message
from backend.app.api.models import InvestigatorRequest
from backend.app.api.routes import investigate


class InvestigatorLocalizationTests(unittest.TestCase):
    def test_request_validation_and_backwards_compatibility(self):
        self.assertEqual(InvestigatorRequest(question="Explain this graph").locale, "en")
        for locale in ("ru", "kk", "en"):
            self.assertEqual(InvestigatorRequest(question="Explain", locale=locale).locale, locale)
        with self.assertRaises(ValidationError):
            InvestigatorRequest(question="Explain", locale="fr")
        with self.assertRaises(ValidationError):
            InvestigatorRequest(question="Explain", selected_gid="not a GID")
        self.assertEqual(len(InvestigatorRequest(question="x" * 1000, selected_gid="123").question), 1000)

    def test_language_policy_survives_tool_round_trips(self):
        gid = "100000004156082100"
        for locale in ("ru", "kk", "en"):
            with self.subTest(locale=locale):
                repository = Mock()
                repository.has_gid.return_value = True
                client = Mock()
                client.responses.create.side_effect = [
                    SimpleNamespace(output=[SimpleNamespace(type="function_call", name="node_card", arguments=json.dumps({"gid": gid}), call_id="call1")]),
                    SimpleNamespace(output=[], output_text="Result " + gid),
                ]
                with patch("backend.app.agent.investigator.MoneyGraphTools") as tools:
                    tools.return_value.execute.return_value = {"referenced_gids": [gid]}
                    result = MoneyGraphInvestigator(repository, client=client).ask("Question", locale, gid)
                self.assertEqual(result.referenced_gids, [gid])
                self.assertEqual(len(result.tool_calls), 1)
                for call in client.responses.create.call_args_list:
                    self.assertIn(SYSTEM_INSTRUCTIONS, call.kwargs["instructions"])
                    self.assertIn(LANGUAGE_INSTRUCTIONS[locale], call.kwargs["instructions"])
                    self.assertFalse(call.kwargs["store"])
                    self.assertIn(CONTEXT[locale].format(gid=gid), call.kwargs["input"][0]["content"])

    def test_unconfigured_api_localizes_without_constructing_ai_client(self):
        for locale in ("ru", "kk", "en"):
            with patch.dict("os.environ", {"OPENAI_API_KEY": ""}), patch("backend.app.api.routes.MoneyGraphInvestigator") as agent:
                response = investigate(InvestigatorRequest(question="Explain", locale=locale), Mock())
                self.assertEqual(response.status_code, 503)
                self.assertEqual(json.loads(response.body)["answer"], message("unavailable", locale))
                agent.assert_not_called()

    def test_route_forwards_locale_and_selected_gid(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-only"}), patch("backend.app.api.routes.MoneyGraphInvestigator") as agent:
            investigate(InvestigatorRequest(question="Question", locale="kk", selected_gid="123"), Mock())
            agent.return_value.ask.assert_called_once_with("Question", locale="kk", selected_gid="123")

    def test_empty_and_ungrounded_answers_are_localized(self):
        for locale in ("ru", "kk", "en"):
            self.assertEqual(MoneyGraphInvestigator._validate_answer_gids("Unknown 999999999999999999", set(), locale), message("ungrounded", locale))
            client = Mock()
            client.responses.create.return_value = SimpleNamespace(output=[], output_text="")
            with patch("backend.app.agent.investigator.MoneyGraphTools"):
                result = MoneyGraphInvestigator(Mock(), client=client).ask("Question", locale)
            self.assertEqual(result.answer, message("empty", locale))


if __name__ == "__main__":
    unittest.main()
