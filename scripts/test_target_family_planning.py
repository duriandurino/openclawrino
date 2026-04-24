#!/usr/bin/env python3
from __future__ import annotations

import unittest

from scripts.orchestration.plan_target_family import build_plan
from scripts.shared.lib.target_family import compose_family, load_target_families, recommend_target_family


class TargetFamilyPlanningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_target_families()

    def test_player_pulselink_composes_parent_capabilities(self):
        family = compose_family("player-pulselink", data=self.data)
        enum_block = family["phases"]["enum"]
        self.assertIn("mqtt", enum_block["capabilities"])
        self.assertIn("pulselink-http", enum_block["capabilities"])
        self.assertIn("enum-player-pulselink-core", enum_block["manifests"])
        self.assertIn("enum-player-core", enum_block["manifests"])
        self.assertIn("enum-raspi-core", enum_block["manifests"])

    def test_plan_from_hint_keeps_exploit_and_post_separate(self):
        rec = recommend_target_family(
            "Raspberry Pi player kiosk with Electron UI, Python service, MQTT, PulseLink",
            data=self.data,
        )
        self.assertEqual(rec["family"], "player-pulselink")

        plan = build_plan(
            rec["family"],
            target="192.168.0.50",
            engagement="engagements/player-v2",
            data=self.data,
        )
        phases = {phase["phase"]: phase for phase in plan["phases"]}

        exploit_manifests = [item["name"] for item in phases["exploit"]["manifests"]]
        post_manifests = [item["name"] for item in phases["post-exploit"]["manifests"]]

        self.assertEqual(exploit_manifests, ["exploit-evidence-first"])
        self.assertEqual(post_manifests, ["post-evidence-first"])

    def test_unknown_hint_falls_back_to_linux_host(self):
        rec = recommend_target_family("mystery appliance with unclear stack", data=self.data)
        self.assertEqual(rec["family"], "linux-host")
        self.assertIn("raspi", rec["alternatives"])


if __name__ == "__main__":
    unittest.main()
