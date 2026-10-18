"""Behavioral contracts for the educator recipe, not model-learning claims."""
from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import build
import import_curriculum
import verify


class BuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "kit"
        shutil.copytree(build.ROOT, self.root, ignore=shutil.ignore_patterns(".git", ".work", "__pycache__"))

    def profile(self, name: str = "example-school") -> dict:
        return json.loads((self.root / f"profiles/{name}.json").read_bytes())

    def save_profile(self, profile: dict, name: str = "example-school") -> None:
        (self.root / f"profiles/{name}.json").write_bytes(build.encode(profile))

    def export(self, profile: str = "example-school", output: str = "output") -> dict[str, bytes]:
        return build.export(self.root, f"profiles/{profile}.json", self.base / output)

    def test_both_profiles_build_deterministically(self) -> None:
        for profile in ("big-lever", "example-school"):
            first = self.export(profile, profile + "-first")
            second = self.export(profile, profile + "-second")
            self.assertEqual(first, second)
            physical = {p.relative_to(self.base / (profile + "-first")).as_posix() for p in (self.base / (profile + "-first")).rglob("*") if p.is_file()}
            self.assertEqual(physical, set(first))
            self.assertEqual(len([p for p in first if p.endswith("/SKILL.md")]), 2)
            self.assertEqual(len([p for p in first if p.endswith("/instructions.md")]), 2)
            manifest = json.loads(first["release-manifest.json"])
            self.assertEqual(set(manifest["files"]), set(first) - {"release-manifest.json"})
            for name, checksum in manifest["files"].items():
                self.assertEqual(checksum, hashlib.sha256(first[name]).hexdigest())

    def test_every_declared_reference_is_exact_in_both_skills(self) -> None:
        for profile_name in ("big-lever", "example-school"):
            profile = self.profile(profile_name)
            files = self.export(profile_name, profile_name)
            for role in build.ROLES:
                for reference in profile["reference_files"]:
                    expected = (self.root / profile["curriculum_dir"] / reference).read_bytes()
                    path = f"packages/{profile['slug']}-{role}/skills/{profile['slug']}-{role}/references/{reference}"
                    self.assertEqual(files[path], expected)

    def test_curriculum_change_reaches_both_guides_and_authoring_knowledge(self) -> None:
        before = self.export(output="before")
        lesson = self.root / "curriculum/example-school/lessons.md"
        lesson.write_text(lesson.read_text() + "\nNew unique teaching correction.\n")
        after = self.export(output="after")
        for role in build.ROLES:
            ref = f"packages/example-school-{role}/skills/example-school-{role}/references/lessons.md"
            self.assertNotEqual(before[ref], after[ref])
            self.assertIn(b"New unique teaching correction.", after[f"builder/{role}/knowledge.md"])

    def test_school_substitution_has_no_bli_routes_or_feedback(self) -> None:
        files = self.export()
        # Attribution/license notices appropriately keep the original Institute name.
        for name, content in files.items():
            if name.endswith(("kit-notice.md", "kit-license.md", "NOTICE.md", "LICENSE.md", "knowledge.md")):
                continue
            if name == "release-manifest.json":
                continue
            body = content.decode("utf-8")
            self.assertNotIn("Startup Foundations", body)
            self.assertNotIn("bigleverinstitute.org", body)
            self.assertNotIn("Vibe Coding", body)
            self.assertNotIn("help@", body)
        for role in build.ROLES:
            instructions = files[f"builder/{role}/instructions.md"].decode()
            self.assertIn("Example Community Learning Center", instructions)
            self.assertIn("No feedback destination is configured", instructions)
            self.assertIn("No future courses are configured", instructions)

    def test_manifest_shapes_frontmatter_and_reference_links(self) -> None:
        files = self.export("big-lever")
        marketplace = json.loads(files[".claude-plugin/marketplace.json"])
        self.assertEqual(len(marketplace["plugins"]), 2)
        for entry in marketplace["plugins"]:
            prefix = entry["source"].removeprefix("./") + "/"
            manifest = json.loads(files[prefix + "plugin.json"])
            self.assertEqual(manifest["$schema"], build.SCHEMA)
            self.assertEqual(manifest["name"], entry["name"])
            interface = manifest["extensions"]["com.openai"]["interface"]
            self.assertLessEqual(len(interface["shortDescription"]), 30)
            self.assertIsInstance(interface["capabilities"], list)
            self.assertLessEqual(len(interface["defaultPrompt"]), 3)
            skill_path = prefix + f"skills/{entry['name']}/SKILL.md"
            skill = files[skill_path].decode("utf-8")
            front = skill.split("---", 2)[1]
            self.assertIn(f"name: {entry['name']}", front)
            json.loads(front.split("description: ", 1)[1].strip())
            import re
            for relative in re.findall(r"\]\((references/[^)]+)\)", skill):
                self.assertIn(prefix + f"skills/{entry['name']}/" + relative, files)
            self.assertEqual(files[prefix + "LICENSE.md"], (self.root / "LICENSE.md").read_bytes())
        for role in build.ROLES:
            self.assertLessEqual(len(files[f"builder/{role}/instructions.md"].decode()), 8000)

    def test_invalid_profile_variants_fail_before_output(self) -> None:
        original = self.profile()
        changes = [
            {"slug": "../escape"}, {"slug": 3}, {"version": "v1"}, {"version": "01.0.0"}, {"snapshot_date": "yesterday"},
            {"homepage": "http://example.org"}, {"homepage": "https://user:secret@example.org"},
            {"reference_files": ["../escape.md"]}, {"reference_files": []}, {"reference_files": ["lessons.md", "lessons.md"]},
            {"curriculum_index": "missing.md"}, {"future_courses": "planned"}, {"future_courses": [False]},
            {"reference_files": ["missing.md"], "curriculum_index": "missing.md"},
            {"feedback_email": "not-an-address"}, {"organization": "Two\nlines"}, {"unknown": True},
        ]
        for change in changes:
            with self.subTest(change=change):
                profile = deepcopy(original)
                profile.update(change)
                self.save_profile(profile)
                with self.assertRaises(ValueError):
                    self.export()
                self.assertFalse((self.base / "output").exists())

    def test_invalid_json_and_profile_roots_fail_clearly(self) -> None:
        for data in (b"{broken", b"[]", b"null"):
            (self.root / "profiles/example-school.json").write_bytes(data)
            with self.assertRaises(ValueError):
                self.export()
            self.assertFalse((self.base / "output").exists())

    def test_malformed_curriculum_json_is_rejected(self) -> None:
        (self.root / "curriculum/example-school/catalog.json").write_text("{bad")
        with self.assertRaises(ValueError):
            self.export()
        self.assertFalse((self.base / "output").exists())

    def test_catalog_rejects_missing_bodies_duplicate_ids_and_date_drift(self) -> None:
        path = self.root / "curriculum/example-school/catalog.json"
        original = json.loads(path.read_bytes())
        variants = []
        for field, value in (("source_heading", "Missing body"), ("url", "http://example.org"), ("title", "")):
            changed = deepcopy(original)
            changed["resources"][0][field] = value
            variants.append(changed)
        duplicate = deepcopy(original)
        duplicate["resources"].append(duplicate["resources"][0])
        variants.extend([duplicate, {"snapshot_date": "2020-01-01", "resources": original["resources"]}, {"snapshot_date": original["snapshot_date"], "resources": []}])
        for changed in variants:
            path.write_bytes(build.encode(changed))
            with self.assertRaises(ValueError):
                self.export()
            self.assertFalse((self.base / "output").exists())

    def test_symlinked_file_and_parent_are_rejected(self) -> None:
        path = self.root / "curriculum/example-school/lessons.md"
        path.unlink()
        path.symlink_to(self.root / "README.md")
        with self.assertRaises(ValueError):
            self.export()
        path.unlink()
        source = self.root / "curriculum/example-school"
        source.rename(self.root / "moved-example")
        source.symlink_to(self.root / "moved-example", target_is_directory=True)
        with self.assertRaises(ValueError):
            self.export()
        self.assertFalse((self.base / "output").exists())

    def test_output_preservation_and_symlink_parents(self) -> None:
        output = self.base / "existing"
        output.mkdir()
        (output / "keep").write_bytes(b"original")
        with self.assertRaises(ValueError):
            build.export(self.root, "profiles/example-school.json", output)
        self.assertEqual((output / "keep").read_bytes(), b"original")
        for path in (self.root, self.root / "nested", self.base):
            with self.assertRaises(ValueError):
                build.export(self.root, "profiles/example-school.json", path)
        (self.base / "alias").symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(ValueError):
            build.export(self.root, "profiles/example-school.json", self.base / "alias" / "fresh")
        self.assertFalse((self.base / "fresh").exists())

    def test_unknown_tokens_fail_without_partial_output(self) -> None:
        template = self.root / "templates/common.md"
        template.write_text(template.read_text() + "\n{{missing_setting}}\n")
        with self.assertRaises(ValueError):
            self.export()
        self.assertFalse((self.base / "output").exists())

    def test_verifier_rejects_edits_deletions_extras_and_manifest_forgery(self) -> None:
        expected = build.artifacts(self.root, "profiles/big-lever.json")
        for name, content in expected.items():
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        verify.verify(self.root)
        target = self.root / "builder/guide-me/instructions.md"
        original = target.read_bytes()
        for mode in ("edit", "delete", "extra", "forged-hash"):
            with self.subTest(mode=mode):
                target.write_bytes(original)
                extra = self.root / "packages/unreviewed.txt"
                if mode in {"edit", "forged-hash"}:
                    target.write_bytes(b"Changed behavior")
                elif mode == "delete":
                    target.unlink()
                else:
                    extra.write_text("Unexpected file")
                if mode == "forged-hash":
                    manifest = json.loads((self.root / "release-manifest.json").read_bytes())
                    manifest["files"]["builder/guide-me/instructions.md"] = hashlib.sha256(target.read_bytes()).hexdigest()
                    (self.root / "release-manifest.json").write_bytes(build.encode(manifest))
                with self.assertRaises(ValueError):
                    verify.verify(self.root)
                if extra.exists():
                    extra.unlink()

    def test_curriculum_teaching_license_and_prior_rights_reach_both_guides(self) -> None:
        files = self.export("big-lever")
        for role in build.ROLES:
            prefix = f"packages/big-lever-{role}/"
            license_text = files[prefix + "LICENSE.md"].decode()
            self.assertIn("Permission for teaching", license_text)
            self.assertIn("Do not repackage for sale, resell", license_text)
            self.assertIn("Learner-created work", license_text)
            upstream_license = files[prefix + f"skills/big-lever-{role}/references/LICENSE.md"]
            self.assertTrue(upstream_license.startswith(b"# Big Lever Educator Teaching-Use License"))
            self.assertIn(b"regardless of which copy is used", upstream_license)
            self.assertIn(b"Do not repackage for sale, resell", upstream_license)
            self.assertIn(upstream_license, files[f"builder/{role}/knowledge.md"])
            self.assertNotEqual(upstream_license, files[prefix + "LICENSE.md"])

    def test_cli_success_and_failure_exit_codes(self) -> None:
        success = subprocess.run([sys.executable, str(self.root / "tools/build.py"), "--profile", "profiles/example-school.json", "--output", str(self.base / "cli")], capture_output=True, text=True)
        self.assertEqual(success.returncode, 0, success.stderr)
        repeat = subprocess.run([sys.executable, str(self.root / "tools/build.py"), "--output", str(self.base / "cli")], capture_output=True, text=True)
        self.assertEqual(repeat.returncode, 2)
        self.assertIn("Build failed", repeat.stderr)

    def test_import_resolves_relative_links_without_changing_prose(self) -> None:
        body = '[Lesson](../basics/a.md) <a href="../curriculum.md">Map</a> [External](https://example.org)'
        actual = import_curriculum.resolve_links(body, 'https://github.com/org/repo/blob/abc/exercises/x.md')
        self.assertIn('https://github.com/org/repo/blob/abc/basics/a.md', actual)
        self.assertIn('href="https://github.com/org/repo/blob/abc/curriculum.md"', actual)
        self.assertIn('[External](https://example.org)', actual)
        self.assertIn('>Map</a>', actual)

    def test_reference_names_with_spaces_or_punctuation_fail_clearly(self) -> None:
        original = self.profile()
        for filename in ("Lesson 1.md", "lesson(1).md", "lesson[1].md"):
            profile = deepcopy(original)
            profile["reference_files"].append(filename)
            self.save_profile(profile)
            with self.assertRaisesRegex(ValueError, "Reference paths may use only"):
                self.export()
            self.assertFalse((self.base / "output").exists())

    def test_reserved_reference_prefixes_fail_before_output_creation(self) -> None:
        original = self.profile()
        for reserved in ("kit-context.md", "kit-license.md", "kit-notice.md", "KIT-CONTEXT.md"):
            name = reserved + "/notes.md"
            path = self.root / "curriculum/example-school" / name
            path.parent.mkdir(exist_ok=True)
            path.write_text("This directory must not collide with generated context.")
            profile = deepcopy(original)
            profile["reference_files"].append(name)
            self.save_profile(profile)
            with self.assertRaisesRegex(ValueError, "Reference path collision"):
                self.export()
            self.assertFalse((self.base / "output").exists())

    def test_case_insensitive_reference_duplicates_are_rejected(self) -> None:
        profile = self.profile()
        profile["reference_files"].append("LESSONS.md")
        self.save_profile(profile)
        with self.assertRaisesRegex(ValueError, "Reference path collision"):
            self.export()
        self.assertFalse((self.base / "output").exists())

    def test_reference_directory_aliases_and_source_case_fail_before_output(self) -> None:
        profile = self.profile()
        extra = self.root / "curriculum/example-school/Extra"
        extra.mkdir()
        (extra / "a.md").write_text("First")
        (extra / "b.md").write_text("Second")
        profile["reference_files"].extend(["Extra/a.md", "extra/b.md"])
        self.save_profile(profile)
        with self.assertRaisesRegex(ValueError, "Reference path collision"):
            self.export()
        self.assertFalse((self.base / "output").exists())
        profile["reference_files"] = [name for name in profile["reference_files"] if not name.startswith(("Extra/", "extra/"))]
        self.save_profile(profile)
        source = self.root / "curriculum/example-school/lessons.md"
        source.rename(source.with_name("Lessons.md"))
        with self.assertRaisesRegex(ValueError, "filename spelling/case"):
            self.export()
        self.assertFalse((self.base / "output").exists())

    def test_alternate_distribution_verifies_only_against_its_profile(self) -> None:
        for name in ("packages", "builder", ".claude-plugin"):
            shutil.rmtree(self.root / name)
        for name, data in build.artifacts(self.root, "profiles/example-school.json").items():
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        verify.verify(self.root, "profiles/example-school.json")
        with self.assertRaisesRegex(ValueError, "Generated files differ"):
            verify.verify(self.root)
        result = subprocess.run([sys.executable, str(self.root / "tools/verify.py"), "--profile", "profiles/example-school.json"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_public_import_checks_pinned_commit_and_dirty_source(self) -> None:
        source = self.base / "public-source"
        source.mkdir()
        upstream = json.loads((self.root / "curriculum/big-lever/upstream.json").read_bytes())
        resolved_license = (self.root / "curriculum/big-lever/LICENSE.md").read_text()
        raw_license = resolved_license.replace(f"{import_curriculum.REPOSITORY}/blob/{upstream['commit']}/tools/LICENSE", "tools/LICENSE")
        raw_license = raw_license.replace(f"{import_curriculum.REPOSITORY}/blob/{upstream['commit']}/LICENSE-CC-BY-4.0.md", "LICENSE-CC-BY-4.0.md")
        contents = {"basics/a.md": "# A\n\n[Next](../curriculum.md)\n", "LICENSE.md": raw_license}
        for name in import_curriculum.PEDAGOGY:
            contents[name] = "# Teaching reference\n"
        for name, content in contents.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        inventory = {"release_date": "2026-10-17", "pages": [{"path": "basics/a.md", "title": "A", "group": "AI Basics", "browser_path": "site/basics/a.html"}],
                     "files": {name: hashlib.sha256(content.encode()).hexdigest() for name, content in contents.items()}}
        (source / "release-manifest.json").write_bytes(build.encode(inventory))
        subprocess.run(["git", "init", "-q", str(source)], check=True)
        subprocess.run(["git", "-C", str(source), "add", "."], check=True)
        subprocess.run(["git", "-C", str(source), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.org", "commit", "-qm", "fixture"], check=True)
        commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
        collected = import_curriculum.collect(source, commit)
        self.assertEqual(json.loads(collected["upstream.json"])["commit"], commit)
        self.assertIn(b"https://github.com/BigLeverVentures/bli-for-educators/blob/", collected["lessons.md"])
        with self.assertRaisesRegex(ValueError, "does not match"):
            import_curriculum.collect(source, "0" * 40)
        # Rehash and commit each mutation so it reaches the license gate, not an integrity gate.
        for forged in ("Creative Commons Attribution 4.0\nNo resale.\n", "# Big Lever Educator Teaching-Use License — Version 1.0\nUnreviewed terms.\n", raw_license + "\nUnreviewed condition.\n"):
            (source / "LICENSE.md").write_text(forged)
            inventory["files"]["LICENSE.md"] = hashlib.sha256(forged.encode()).hexdigest()
            (source / "release-manifest.json").write_bytes(build.encode(inventory))
            subprocess.run(["git", "-C", str(source), "add", "."], check=True)
            subprocess.run(["git", "-C", str(source), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.org", "commit", "-qm", "license mutation"], check=True)
            mutated_commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
            with self.assertRaisesRegex(ValueError, "Unreviewed upstream license"):
                import_curriculum.collect(source, mutated_commit)
        # Restore reviewed bytes as a new committed fixture for the independent dirty-source check.
        (source / "LICENSE.md").write_text(raw_license)
        inventory["files"]["LICENSE.md"] = hashlib.sha256(raw_license.encode()).hexdigest()
        (source / "release-manifest.json").write_bytes(build.encode(inventory))
        subprocess.run(["git", "-C", str(source), "add", "."], check=True)
        subprocess.run(["git", "-C", str(source), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.org", "commit", "-qm", "restore reviewed license"], check=True)
        commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
        (source / "basics/a.md").write_text("uncommitted change")
        with self.assertRaisesRegex(ValueError, "differs from the pinned"):
            import_curriculum.collect(source, commit)

    def test_coaching_fixture_inventory_and_source_policy(self) -> None:
        cases = json.loads((self.root / "tests/coaching-cases.json").read_bytes())
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        self.assertTrue({"direct-help", "critique-choice", "execution-only", "small-path", "future-course", "missing-source"}.issubset({case["id"] for case in cases}))
        for case in cases:
            self.assertIn(case["guide"], build.ROLES)
            self.assertTrue(case["prompt"] and case["expect"] and case["fail"])

    def test_local_documentation_links_resolve(self) -> None:
        docs = [self.root / "README.md", self.root / "NOTICE.md", self.root / "CONTRIBUTING.md", *self.root.glob("docs/*.md")]
        for path in docs:
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" in link or link.startswith(("#", "mailto:")):
                    continue
                target = link.split("#", 1)[0]
                self.assertTrue((path.parent / target).exists(), f"Broken link in {path.name}: {link}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
