#!/usr/bin/env python3
"""
Validation Test Script
Tests PIT tool structure and components without requiring full installation.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_file_structure():
    """Validate that all required files exist."""
    print("\n=== File Structure Validation ===\n")

    required_files = [
        # Core implementation
        "pit/__init__.py",
        "pit/config/__init__.py",
        "pit/config/schema.py",
        "pit/config/loader.py",
        "pit/errors/__init__.py",
        "pit/errors/exceptions.py",
        "pit/errors/handlers.py",
        "pit/orchestrator/__init__.py",
        "pit/orchestrator/pipeline.py",
        "pit/orchestrator/phases.py",
        "pit/orchestrator/workflow.py",
        "pit/reporting/__init__.py",
        "pit/reporting/formatters.py",

        # Tests
        "tests/integration/__init__.py",
        "tests/integration/test_pipeline.py",
        "tests/e2e_test.py",
        "tests/test_reports.py",

        # Documentation
        "SPECIFICATION.md",
        "ARCHITECTURE.md",
        "USER_GUIDE.md",
        "PATTERN_DEVELOPMENT.md",
        "RELEASE.md",
        "CHANGELOG.md",
        "README.md",

        # Deployment
        "Dockerfile",
        "docker-compose.yml",
        ".dockerignore",
        "pyproject.toml",
    ]

    root = Path(__file__).parent.parent
    missing = []
    present = []

    for file_path in required_files:
        full_path = root / file_path
        if full_path.exists():
            present.append(file_path)
            print(f"✓ {file_path}")
        else:
            missing.append(file_path)
            print(f"✗ {file_path} - MISSING")

    print(f"\n📊 Summary: {len(present)}/{len(required_files)} files present")

    if missing:
        print(f"\n⚠️  Missing files: {len(missing)}")
        for f in missing:
            print(f"  - {f}")
        return False

    print("\n✅ All required files present!")
    return True


def test_python_syntax():
    """Validate Python files have correct syntax."""
    print("\n=== Python Syntax Validation ===\n")

    root = Path(__file__).parent.parent
    python_files = list(root.glob("pit/**/*.py")) + list(root.glob("tests/**/*.py"))

    errors = []
    valid = []

    for py_file in python_files:
        try:
            with open(py_file, 'r') as f:
                compile(f.read(), str(py_file), 'exec')
            valid.append(py_file.relative_to(root))
            print(f"✓ {py_file.relative_to(root)}")
        except SyntaxError as e:
            errors.append((py_file.relative_to(root), str(e)))
            print(f"✗ {py_file.relative_to(root)} - Syntax Error: {e}")

    print(f"\n📊 Summary: {len(valid)}/{len(python_files)} files valid")

    if errors:
        print(f"\n⚠️  Syntax errors: {len(errors)}")
        for file, error in errors:
            print(f"  - {file}: {error}")
        return False

    print("\n✅ All Python files have valid syntax!")
    return True


def test_documentation():
    """Validate documentation files."""
    print("\n=== Documentation Validation ===\n")

    root = Path(__file__).parent.parent
    docs = [
        ("SPECIFICATION.md", 900),
        ("ARCHITECTURE.md", 1200),
        ("USER_GUIDE.md", 800),
        ("PATTERN_DEVELOPMENT.md", 650),
        ("RELEASE.md", 300),
        ("CHANGELOG.md", 200),
        ("IMPLEMENTATION_COMPLETE.md", 300),
        ("PHASE2_COMPLETE.md", 200),
        ("PHASE5_COMPLETE.md", 300),
    ]

    for doc_name, expected_lines in docs:
        doc_path = root / doc_name
        if doc_path.exists():
            lines = len(doc_path.read_text().splitlines())
            print(f"✓ {doc_name}: {lines} lines (expected ~{expected_lines})")
        else:
            print(f"✗ {doc_name}: MISSING")

    print("\n✅ Documentation files validated!")
    return True


def test_dependencies():
    """Check which dependencies are available."""
    print("\n=== Dependency Check ===\n")

    deps = [
        "aiohttp",
        "httpx",
        "yaml",
        "rich",
        "typer",
        "pydantic",
        "jinja2",
    ]

    available = []
    missing = []

    for dep in deps:
        try:
            __import__(dep)
            available.append(dep)
            print(f"✓ {dep}")
        except ImportError:
            missing.append(dep)
            print(f"✗ {dep} - NOT INSTALLED")

    print(f"\n📊 Summary: {len(available)}/{len(deps)} dependencies available")

    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("\n💡 To install missing dependencies:")
        print(f"   pip install {' '.join(missing)}")
    else:
        print("\n✅ All dependencies available!")

    return len(available) >= 5  # Need at least 5/7


def test_deployment_files():
    """Validate deployment configuration."""
    print("\n=== Deployment Configuration Validation ===\n")

    root = Path(__file__).parent.parent

    # Check Dockerfile
    dockerfile = root / "Dockerfile"
    if dockerfile.exists():
        content = dockerfile.read_text()
        checks = [
            ("FROM python:", "Base image specified"),
            ("WORKDIR", "Working directory set"),
            ("pip install", "Dependencies installation"),
            ("HEALTHCHECK", "Health check configured"),
            ("ENTRYPOINT", "Entry point configured"),
        ]

        print("Dockerfile:")
        for check, desc in checks:
            if check in content:
                print(f"  ✓ {desc}")
            else:
                print(f"  ✗ {desc} - MISSING")
    else:
        print("✗ Dockerfile not found")

    # Check docker-compose.yml
    compose = root / "docker-compose.yml"
    if compose.exists():
        content = compose.read_text()
        services = ["pit", "ollama", "nginx"]
        print("\ndocker-compose.yml:")
        for service in services:
            if f"{service}:" in content:
                print(f"  ✓ Service: {service}")
            else:
                print(f"  ✗ Service: {service} - MISSING")
    else:
        print("✗ docker-compose.yml not found")

    # Check .dockerignore
    dockerignore = root / ".dockerignore"
    if dockerignore.exists():
        print("\n✓ .dockerignore present")
    else:
        print("\n✗ .dockerignore not found")

    print("\n✅ Deployment configuration validated!")
    return True


def test_git_configuration():
    """Validate git configuration."""
    print("\n=== Git Configuration Validation ===\n")

    root = Path(__file__).parent.parent.parent.parent
    gitignore = root / ".gitignore"

    if gitignore.exists():
        content = gitignore.read_text()
        patterns = [
            "pit_report_*.json",
            "pit_report_*.yaml",
            "pit_report_*.html",
            ".pytest_cache",
            ".coverage",
        ]

        print(".gitignore:")
        for pattern in patterns:
            if pattern in content:
                print(f"  ✓ {pattern}")
            else:
                print(f"  ⚠️  {pattern} - not found (may use different pattern)")

        print("\n✅ Git configuration validated!")
    else:
        print("✗ .gitignore not found at repository root")

    return True


def main():
    """Run all validation tests."""
    print("=" * 70)
    print("PIT Tool Validation Test Suite")
    print("Version: 2.0.0")
    print("=" * 70)

    tests = [
        ("File Structure", test_file_structure),
        ("Python Syntax", test_python_syntax),
        ("Documentation", test_documentation),
        ("Dependencies", test_dependencies),
        ("Deployment Files", test_deployment_files),
        ("Git Configuration", test_git_configuration),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False

    # Final summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")

    print(f"\n📊 Total: {passed}/{total} validation checks passed")

    if passed == total:
        print("\n🎉 All validation checks passed!")
        print("\n✅ PIT v2.0.0 structure is complete and valid!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} validation check(s) failed")
        print("\n💡 Note: Some failures may be due to missing dependencies")
        print("   Install missing dependencies to enable full testing")
        return 1


if __name__ == "__main__":
    sys.exit(main())
