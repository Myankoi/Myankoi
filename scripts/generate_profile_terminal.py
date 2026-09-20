"""Generate the animated terminal used by the GitHub profile README."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "terminal"
FRAMES = Path("/tmp/r4m-gifos-frames")
USERNAME = "Myankoi"
DEFAULT_LANGUAGES = "TypeScript, Java, Dart, Kotlin"

# gifos reads its configuration while being imported.
os.environ.setdefault("GIFOS_GENERAL_USER_NAME", "r4m")
os.environ.setdefault("GIFOS_GENERAL_FPS", "13")
os.environ.setdefault("GIFOS_GENERAL_LOOP_COUNT", "0")
os.environ.setdefault("GIFOS_GENERAL_COLOR_SCHEME", "gruvbox-dark")
os.environ.setdefault("GIFOS_FILES_FRAME_FOLDER_NAME", str(FRAMES))
os.environ.setdefault("GIFOS_FILES_OUTPUT_GIF_NAME", str(OUTPUT))

import gifos  # noqa: E402  (configuration must be set first)


RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"


@dataclass(frozen=True)
class PublicStats:
    repos: str = "--"
    followers: str = "--"
    stars: str = "--"
    commits: str = "--"
    pull_requests: str = "--"
    languages: str = DEFAULT_LANGUAGES


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Myankoi-profile-readme",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_json(url: str, **params: object) -> object:
    response = requests.get(url, headers=_headers(), params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def fetch_public_stats() -> PublicStats:
    """Fetch public-only stats, falling back gracefully when GitHub is unavailable."""
    try:
        user = _get_json(f"https://api.github.com/users/{USERNAME}")
        repos = _get_json(
            f"https://api.github.com/users/{USERNAME}/repos",
            per_page=100,
            type="owner",
        )

        stars = sum(repo.get("stargazers_count", 0) for repo in repos)
        language_totals: dict[str, int] = {}
        for repo in repos:
            if repo.get("fork"):
                continue
            languages = _get_json(repo["languages_url"])
            for language, amount in languages.items():
                language_totals[language] = language_totals.get(language, 0) + amount

        top_languages = ", ".join(
            name
            for name, _ in sorted(
                language_totals.items(), key=lambda item: item[1], reverse=True
            )[:4]
        )

        commit_search = _get_json(
            "https://api.github.com/search/commits", q=f"author:{USERNAME}"
        )
        pr_search = _get_json(
            "https://api.github.com/search/issues",
            q=f"author:{USERNAME} type:pr",
        )

        return PublicStats(
            repos=str(user.get("public_repos", "--")),
            followers=str(user.get("followers", "--")),
            stars=str(stars),
            commits=str(commit_search.get("total_count", "--")),
            pull_requests=str(pr_search.get("total_count", "--")),
            languages=top_languages or DEFAULT_LANGUAGES,
        )
    except (requests.RequestException, TypeError, KeyError, ValueError) as error:
        print(f"WARNING: GitHub stats unavailable; using fallback values: {error}")
        return PublicStats()


def type_command(terminal: gifos.Terminal, command: str, output: str) -> None:
    row = terminal.curr_row
    terminal.gen_text(
        f"{RED}r4m{YELLOW}@r4mOS {BLUE}~> {RESET}", row, count=2
    )
    terminal.toggle_show_cursor(True)
    terminal.gen_typing_text(f"{GREEN}{command}{RESET}", row, contin=True, speed=1)
    terminal.toggle_show_cursor(False)
    terminal.gen_text(output, row + 1, count=3)


def main() -> None:
    stats = fetch_public_stats()
    terminal = gifos.Terminal(900, 520, 14, 14, font_size=14, line_spacing=3)

    terminal.gen_text("", 1, count=8)
    terminal.toggle_show_cursor(False)
    terminal.gen_text(f"{YELLOW}r4mOS BIOS v4.4{RESET}", 2, count=5)
    terminal.gen_text("Copyright (C) 2026 r4m labs", 3)
    terminal.gen_text(f"{CYAN}Detecting curiosity engine ............... OK{RESET}", 6, count=4)
    terminal.gen_text(f"{CYAN}Mounting /home/r4m/projects .............. OK{RESET}", 7, count=4)
    terminal.gen_text(f"{CYAN}Loading Fedora 44 Workstation ............ OK{RESET}", 8, count=4)
    terminal.gen_text(f"{GREEN}Boot complete. Welcome to my little corner of the internet.{RESET}", 11, count=12)

    terminal.clear_frame()
    terminal.gen_text(f"{YELLOW}r4mOS 4.4 (tty1){RESET}", 1, count=4)
    terminal.gen_text("login: ", 3)
    terminal.toggle_show_cursor(True)
    terminal.gen_typing_text(f"{GREEN}Myankoi{RESET}", 3, contin=True, speed=1)
    terminal.toggle_show_cursor(False)
    terminal.gen_text("Last login: whenever curiosity called", 5, count=5)

    terminal.clear_frame()
    type_command(
        terminal,
        "whoami",
        f"{YELLOW}Muhammad Ramadian Ramadhan{RESET}\n"
        "Final-year vocational student from Jakarta, Indonesia.\n"
        "I turn ideas and everyday problems into software.",
    )
    type_command(
        terminal,
        "cat highlights.txt",
        f"{YELLOW}[LKS]{RESET} 3rd Place - National IT Software Solutions for Business\n"
        f"{BLUE}[FOCUS]{RESET} Desktop / Backend / Android / thoughtful interfaces",
    )
    type_command(
        terminal,
        "stack --grouped",
        f"{GREEN}building:{RESET} C#, .NET, ASP.NET Core, Kotlin, Jetpack Compose, TypeScript\n"
        f"{CYAN}exploring:{RESET} Go, Laravel, Flutter, C++\n"
        f"{MAGENTA}creative:{RESET} UI/UX, interaction design, pixel art",
    )
    type_command(
        terminal,
        "github --stats",
        f"repos {YELLOW}{stats.repos}{RESET}  |  stars {YELLOW}{stats.stars}{RESET}  |  "
        f"commits {YELLOW}{stats.commits}{RESET}  |  PRs {YELLOW}{stats.pull_requests}{RESET}",
    )
    terminal.gen_text("", terminal.curr_row + 1, count=8)

    terminal.clear_frame()
    logo = [
        " ____  _  _   __  __",
        r"|  _ \| || | |  \/  |",
        r"| |_) | || |_| |\/| |",
        r"|  _ <|__   _| |  | |",
        r"|_| \_\  |_| |_|  |_|",
    ]
    for offset, line in enumerate(logo):
        terminal.gen_text(
            f"{YELLOW}{line}{RESET}", 6 + offset, 3, contin=True
        )
    details = rf"""
{YELLOW}r4m@github{RESET}
------------
{CYAN}Name    {RESET} Muhammad Ramadian Ramadhan
{CYAN}From    {RESET} Jakarta, Indonesia
{CYAN}OS      {RESET} Fedora 44 Workstation / Windows 11
{CYAN}Mobile  {RESET} Android / Samsung Galaxy A53 5G
{CYAN}Focus   {RESET} Desktop / Backend / Android
{CYAN}Award   {RESET} National LKS - 3rd Place

{GREEN}Building{RESET} C#, .NET, Kotlin, TypeScript
{BLUE}Learning{RESET} Go, Laravel, Flutter, C++
{MAGENTA}Making {RESET} UI/UX, interactions, pixel art

{YELLOW}GitHub  {RESET} {stats.repos} repos / {stats.stars} stars / {stats.followers} followers
{YELLOW}Activity{RESET} {stats.commits} commits / {stats.pull_requests} pull requests
{YELLOW}Top lang{RESET} {stats.languages}

{CYAN}Contact {RESET} linkedin.com/in/ramadianramadhan
        muhammadramadian079@gmail.com
"""
    terminal.gen_text(details, 2, 38, count=4, contin=True)
    terminal.gen_text(
        f"{GREEN}Thanks for stopping by - let's build something useful.{RESET}",
        26,
        3,
        count=60,
        contin=True,
    )
    terminal.gen_gif()


if __name__ == "__main__":
    main()
