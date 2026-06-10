from __future__ import annotations

import argparse
import tomllib
from dataclasses import dataclass
from pathlib import Path

from packaging.markers import Marker
from packaging.requirements import Requirement

TARGET_PYTHON_VERSION = "3.12"
TARGET_PYTHON_FULL_VERSION = "3.12.0"


@dataclass(frozen=True)
class LockedDependency:
    name: str
    marker: str | None = None


@dataclass(frozen=True)
class LockedPackage:
    name: str
    sdist_url: str
    sdist_sha256: str
    dependencies: tuple[LockedDependency, ...]


@dataclass(frozen=True)
class ResourceGroups:
    common: tuple[str, ...]
    linux_only: tuple[str, ...]
    macos_only: tuple[str, ...]


def _normalize_name(value: str) -> str:
    return str(value).replace("_", "-").lower()


def _target_environment(*, sys_platform: str) -> dict[str, str]:
    platform_system = "Darwin" if sys_platform == "darwin" else "Linux"
    return {
        "extra": "",
        "implementation_name": "cpython",
        "os_name": "posix",
        "platform_python_implementation": "CPython",
        "platform_system": platform_system,
        "python_full_version": TARGET_PYTHON_FULL_VERSION,
        "python_version": TARGET_PYTHON_VERSION,
        "sys_platform": sys_platform,
    }


def _marker_matches(marker: str | None, environment: dict[str, str]) -> bool:
    if not marker:
        return True
    return Marker(marker).evaluate(environment)


def _load_locked_packages(project_root: Path) -> dict[str, LockedPackage]:
    lock_path = project_root / "uv.lock"
    lock_data = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    packages: dict[str, LockedPackage] = {}
    for package in lock_data["package"]:
        sdist = package.get("sdist")
        if not sdist:
            continue
        normalized_name = _normalize_name(package["name"])
        packages[normalized_name] = LockedPackage(
            name=normalized_name,
            sdist_url=sdist["url"],
            sdist_sha256=str(sdist["hash"]).removeprefix("sha256:"),
            dependencies=tuple(
                LockedDependency(
                    name=_normalize_name(dependency["name"]),
                    marker=dependency.get("marker"),
                )
                for dependency in package.get("dependencies", [])
            ),
        )
    return packages


def _load_direct_dependencies(project_root: Path) -> tuple[LockedDependency, ...]:
    pyproject_path = project_root / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    dependencies = pyproject["project"].get("dependencies", [])
    direct_dependencies: list[LockedDependency] = []
    for raw_requirement in dependencies:
        requirement = Requirement(raw_requirement)
        direct_dependencies.append(
            LockedDependency(
                name=_normalize_name(requirement.name),
                marker=str(requirement.marker) if requirement.marker else None,
            )
        )
    return tuple(direct_dependencies)


def _resolve_resources_for_environment(
    direct_dependencies: tuple[LockedDependency, ...],
    locked_packages: dict[str, LockedPackage],
    environment: dict[str, str],
) -> set[str]:
    resolved: set[str] = set()
    pending = [
        dependency.name
        for dependency in direct_dependencies
        if _marker_matches(dependency.marker, environment)
    ]
    while pending:
        package_name = pending.pop()
        if package_name in resolved:
            continue
        package = locked_packages.get(package_name)
        if package is None:
            raise KeyError(
                f"Missing locked package for Homebrew resource: {package_name}"
            )
        resolved.add(package_name)
        for dependency in package.dependencies:
            if _marker_matches(dependency.marker, environment):
                pending.append(dependency.name)
    return resolved


def resolve_resource_groups(
    project_root: Path,
) -> tuple[ResourceGroups, dict[str, LockedPackage]]:
    direct_dependencies = _load_direct_dependencies(project_root)
    locked_packages = _load_locked_packages(project_root)
    macos_resources = _resolve_resources_for_environment(
        direct_dependencies,
        locked_packages,
        _target_environment(sys_platform="darwin"),
    )
    linux_resources = _resolve_resources_for_environment(
        direct_dependencies,
        locked_packages,
        _target_environment(sys_platform="linux"),
    )
    common = tuple(sorted(macos_resources & linux_resources))
    linux_only = tuple(sorted(linux_resources - macos_resources))
    macos_only = tuple(sorted(macos_resources - linux_resources))
    return (
        ResourceGroups(
            common=common,
            linux_only=linux_only,
            macos_only=macos_only,
        ),
        locked_packages,
    )


def _render_resource_block(package: LockedPackage, *, indent: str = "  ") -> str:
    return (
        f'{indent}resource "{package.name}" do\n'
        f'{indent}  url "{package.sdist_url}"\n'
        f'{indent}  sha256 "{package.sdist_sha256}"\n'
        f"{indent}end"
    )


def _render_resource_section(
    package_names: tuple[str, ...],
    locked_packages: dict[str, LockedPackage],
    *,
    indent: str = "  ",
) -> str:
    if not package_names:
        return ""
    return "\n\n".join(
        _render_resource_block(locked_packages[package_name], indent=indent)
        for package_name in package_names
    )


def build_formula(version: str, sha256: str, repo: str, project_root: Path) -> str:
    release_url = (
        f"https://github.com/{repo}/releases/download/v{version}/"
        f"sanka_cli-{version}.tar.gz"
    )
    test_command = '#{bin}/sanka auth status 2>&1'
    resource_groups, locked_packages = resolve_resource_groups(project_root)
    common_resources = _render_resource_section(resource_groups.common, locked_packages)
    linux_resources = _render_resource_section(
        resource_groups.linux_only,
        locked_packages,
        indent="    ",
    )
    macos_resources = _render_resource_section(
        resource_groups.macos_only,
        locked_packages,
        indent="    ",
    )
    resource_sections: list[str] = []
    if linux_resources:
        resource_sections.append(f"  on_linux do\n{linux_resources}\n  end")
    if macos_resources:
        resource_sections.append(f"  on_macos do\n{macos_resources}\n  end")
    if common_resources:
        resource_sections.append(common_resources)
    rendered_resources = ""
    if resource_sections:
        rendered_resources = "\n\n" + "\n\n".join(resource_sections)

    return f"""class Sanka < Formula
  include Language::Python::Virtualenv

  desc "Thin command-line wrapper for the Sanka API"
  homepage "https://github.com/{repo}"
  url "{release_url}"
  sha256 "{sha256}"
  license "MIT"

  depends_on "python@3.12"{rendered_resources}

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "No access token configured", shell_output("{test_command}", 1)
  end
end
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--repo", default="sankaHQ/sanka-cli")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parent.parent

    Path(args.output).write_text(
        build_formula(args.version, args.sha256, args.repo, project_root),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
