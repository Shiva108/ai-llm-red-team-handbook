#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import textwrap
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BUILD = ROOT / "build" / "handbook_pdf"
CHAPTERS_DIR = BUILD / "chapters"
OUTPUT_PDF = ROOT / "AI_LLM_Red_Team_Handbook.pdf"
OUTPUT_TEX = BUILD / "handbook.tex"
HEADER_TEX = BUILD / "book-header.tex"
FRONTMATTER_MD = BUILD / "00_frontmatter.md"

CHAPTER_FILES = [
    "Chapter_01_Introduction_to_AI_Red_Teaming.md",
    "Chapter_02_Ethics_Legal_and_Stakeholder_Communication.md",
    "Chapter_03_The_Red_Teamers_Mindset.md",
    "Chapter_04_SOW_Rules_of_Engagement_and_Client_Onboarding.md",
    "Chapter_05_Threat_Modeling_and_Risk_Analysis.md",
    "Chapter_06_Scoping_an_Engagement.md",
    "Chapter_07_Lab_Setup_and_Environmental_Safety.md",
    "Chapter_08_Evidence_Documentation_and_Chain_of_Custody.md",
    "Chapter_09_LLM_Architectures_and_System_Components.md",
    "Chapter_10_Tokenization_Context_and_Generation.md",
    "Chapter_11_Plugins_Extensions_and_External_APIs.md",
    "Chapter_12_Retrieval_Augmented_Generation_RAG_Pipelines.md",
    "Chapter_13_Data_Provenance_and_Supply_Chain_Security.md",
    "Chapter_14_Prompt_Injection.md",
    "Chapter_15_Data_Leakage_and_Extraction.md",
    "Chapter_16_Jailbreaks_and_Bypass_Techniques.md",
    "Chapter_17_01_Fundamentals_and_Architecture.md",
    "Chapter_17_02_API_Authentication_and_Authorization.md",
    "Chapter_17_03_Plugin_Vulnerabilities.md",
    "Chapter_17_04_API_Exploitation_and_Function_Calling.md",
    "Chapter_17_05_Third_Party_Risks_and_Testing.md",
    "Chapter_17_06_Case_Studies_and_Defense.md",
    "Chapter_18_Evasion_Obfuscation_and_Adversarial_Inputs.md",
    "Chapter_19_Training_Data_Poisoning.md",
    "Chapter_20_Model_Theft_and_Membership_Inference.md",
    "Chapter_21_Model_DoS_Resource_Exhaustion.md",
    "Chapter_22_Cross_Modal_Multimodal_Attacks.md",
    "Chapter_23_Advanced_Persistence_Chaining.md",
    "Chapter_24_Social_Engineering_LLMs.md",
    "Chapter_25_Advanced_Adversarial_ML.md",
    "Chapter_26_Supply_Chain_Attacks_on_AI.md",
    "Chapter_27_Federated_Learning_Attacks.md",
    "Chapter_28_AI_Privacy_Attacks.md",
    "Chapter_29_Model_Inversion_Attacks.md",
    "Chapter_30_Backdoor_Attacks.md",
    "Chapter_31_AI_System_Reconnaissance.md",
    "Chapter_32_Automated_Attack_Frameworks.md",
    "Chapter_33_Red_Team_Automation.md",
    "Chapter_34_Defense_Evasion_Techniques.md",
    "Chapter_35_Post-Exploitation_in_AI_Systems.md",
    "Chapter_36_Reporting_and_Communication.md",
    "Chapter_37_Remediation_Strategies.md",
    "Chapter_38_Continuous_Red_Teaming.md",
    "Chapter_39_AI_Bug_Bounty_Programs.md",
    "Chapter_40_Compliance_and_Standards.md",
    "Chapter_41_Industry_Best_Practices.md",
    "Chapter_42_Case_Studies_and_War_Stories.md",
    "Chapter_43_Future_of_AI_Red_Teaming.md",
    "Chapter_44_Emerging_Threats.md",
    "Chapter_45_Building_an_AI_Red_Team_Program.md",
    "Chapter_46_Conclusion_and_Next_Steps.md",
]

BROKEN_IMAGE_MAP = {
    "docs/assets/rec28_jailbreak_vs_injection_matrix.png": "docs/assets/rec28_jailbreak_vs_injection.png",
    "docs/assets/rec29_alignment_tension_diagram.png": "docs/assets/rec29_alignment_tension.png",
    "docs/assets/rec30_trust_map_diagram.png": "docs/assets/rec30_trust_map.png",
    "docs/assets/rec31_function_injection_diagram.png": "docs/assets/rec31_function_injection.png",
    "docs/assets/rec32_tokenization_gap_diagram.png": "docs/assets/rec32_tokenization_gap.png",
    "docs/assets/rec33_evasion_spectrum_matrix.png": "docs/assets/rec33_evasion_spectrum.png",
    "docs/assets/rec34_gcg_optimization_flow.png": "docs/assets/rec34_gcg_optimization.png",
    "docs/assets/rec35_poisoned_training_flow.png": "docs/assets/rec35_poisoned_training.png",
    "docs/assets/rec36_model_task_superposition.png": "docs/assets/rec36_superposition.png",
    "docs/assets/rec37_backdoor_activation_sequence.png": "docs/assets/rec37_backdoor_activation.png",
    "docs/assets/rec38_supply_chain_poisoning_map.png": "docs/assets/rec38_poisoning_map.png",
    "docs/assets/rec39_model_extraction_flow.png": "docs/assets/rec39_model_extraction.png",
    "docs/assets/rec40_mia_architecture_diagram.png": "docs/assets/rec40_mia_architecture.png",
}

MERMAID_REPLACEMENTS = {
    ("Chapter_07_Lab_Setup_and_Environmental_Safety.md", 0): (
        "![Logical topology for a standard isolated red team lab.](docs/assets/chapter_07_simple_topology_diagram.png){ width=78% }\n"
    ),
    ("Chapter_18_Evasion_Obfuscation_and_Adversarial_Inputs.md", 0): "",
    ("Chapter_42_Case_Studies_and_War_Stories.md", 0): (
        "![RAG hallucination failure flow.](docs/assets/Ch42_Flow_RAGFailure.png){ width=78% }\n"
    ),
    ("Chapter_45_Building_an_AI_Red_Team_Program.md", 0): "",
    ("Chapter_45_Building_an_AI_Red_Team_Program.md", 1): "",
    ("Chapter_46_Conclusion_and_Next_Steps.md", 0): "",
    ("Chapter_46_Conclusion_and_Next_Steps.md", 1): "",
}

ADMONITION_LABELS = {
    "NOTE": "Note",
    "TIP": "Tip",
    "IMPORTANT": "Important",
    "WARNING": "Warning",
    "CAUTION": "Caution",
}


def ensure_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Missing required tool: {name}")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def normalize_asset_paths(text: str) -> str:
    text = text.replace('src="/docs/assets/', 'src="docs/assets/')
    text = text.replace("](/docs/assets/", "](docs/assets/")
    text = text.replace('src="assets/', 'src="docs/assets/')
    text = text.replace("](assets/", "](docs/assets/")
    for broken, fixed in BROKEN_IMAGE_MAP.items():
        text = text.replace(broken, fixed)
    return text


def normalize_unicode(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    replacements = {
        "\ufe0f": "",
        "✅": "[OK]",
        "❌": "[X]",
        "🚨": "Alert:",
        "📝": "Note:",
        "➔": "->",
        "⚠": "[!]",
        "🔴": "[Red]",
        "🔥": "[Fire]",
        "🛡": "[Shield]",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def strip_local_md_links(text: str) -> str:
    pattern = re.compile(r"\[([^\]]+)\]\((?!https?://)([^)]+\.md(?:#[^)]+)?)\)")
    return pattern.sub(lambda m: m.group(1), text)


def convert_callouts(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^>\s*\[!([A-Z]+)\]\s*(.*)$", line)
        if not m:
            out.append(line)
            i += 1
            continue

        label = ADMONITION_LABELS.get(m.group(1), m.group(1).title())
        rest = m.group(2).strip()
        if rest.startswith(">"):
            rest = rest[1:].strip()

        block = [f"> **{label}.**" + (f" {rest}" if rest else "")]
        i += 1
        while i < len(lines) and lines[i].startswith(">"):
            content = lines[i][1:]
            if content.startswith(" "):
                content = content[1:]
            block.append(f"> {content}")
            i += 1
        out.extend(block)
    return "\n".join(out) + "\n"


def convert_centered_images(text: str) -> str:
    pattern = re.compile(r"<p\s+align=\"center\">\s*(<img\s+[^>]+>)\s*</p>", re.IGNORECASE | re.DOTALL)

    def repl(match: re.Match[str]) -> str:
        tag = match.group(1)
        src_match = re.search(r'src="([^"]+)"', tag, re.IGNORECASE)
        alt_match = re.search(r'alt="([^"]*)"', tag, re.IGNORECASE)
        if not src_match:
            return match.group(0)
        src = src_match.group(1)
        caption = alt_match.group(1).strip() if alt_match else ""
        label = f"![{caption}]({src})" if caption else f"![]({src})"
        return f"{label}{{ width=74% }}\n"

    return pattern.sub(repl, text)


def replace_mermaid_blocks(filename: str, text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    block_index = 0
    while i < len(lines):
        if lines[i].startswith("```mermaid"):
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                i += 1
            if i < len(lines):
                i += 1
            replacement = MERMAID_REPLACEMENTS.get((filename, block_index), "")
            if replacement:
                out.append(replacement)
                if not replacement.endswith("\n"):
                    out.append("\n")
            block_index += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out)


def cleanup_spacing(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def preprocess_markdown(filename: str, raw_text: str) -> str:
    text = normalize_unicode(raw_text.replace("\r\n", "\n"))
    text = normalize_asset_paths(text)
    text = strip_local_md_links(text)
    text = convert_centered_images(text)
    text = replace_mermaid_blocks(filename, text)
    text = convert_callouts(text)
    text = cleanup_spacing(text)
    return text


def frontmatter_markdown() -> str:
    return textwrap.dedent(
        r"""
        ---
        title-meta: "AI LLM Red Team Handbook"
        author-meta: "Shiva108"
        date-meta: "April 2026"
        lang: "en-US"
        papersize: "a4"
        documentclass: "book"
        classoption:
          - "11pt"
          - "oneside"
          - "openany"
        colorlinks: true
        linkcolor: black
        urlcolor: black
        toc-depth: 2
        secnumdepth: 3
        ---

        ```{=latex}
        \frontmatter
        \begin{titlepage}
        \thispagestyle{empty}
        \centering
        \vspace*{1.2cm}
        \includegraphics[width=0.94\textwidth]{docs/assets/cover_1920.png}

        \vspace{1.8cm}
        {\Huge\bfseries AI LLM Red Team Handbook\par}
        \vspace{0.5cm}
        {\Large The Complete Consultant's Guide to AI \& LLM Security Testing\par}
        \vspace{1.2cm}
        {\large Shiva108\par}
        \vfill
        {\large April 2026\par}
        \end{titlepage}

        \clearpage
        \thispagestyle{empty}
        \null
        \vfill
        \begin{center}
        {\Large About This Edition\par}
        \end{center}
        \vspace{1em}
        This publication consolidates the full handbook into a single print-style volume.
        It preserves the original chapter order, illustrations, and technical material while
        reformatting the content for continuous reading and offline distribution.

        \vspace{1em}
        \noindent\textbf{Authorized use only.} The techniques documented in this book are intended
        for defensive research, training, and authorized security testing.
        \clearpage

        \pdfbookmark[0]{Contents}{contents}
        \tableofcontents
        \clearpage
        \mainmatter
        ```
        """
    ).strip() + "\n"


def latex_header() -> str:
    return textwrap.dedent(
        r"""
        \usepackage[a4paper,margin=1in,headheight=16pt]{geometry}
        \usepackage{graphicx}
        \usepackage{float}
        \usepackage{booktabs}
        \usepackage{longtable}
        \usepackage{array}
        \usepackage{caption}
        \usepackage{fancyhdr}
        \usepackage{titlesec}
        \usepackage{etoolbox}
        \usepackage{fvextra}
        \usepackage{microtype}
        \usepackage{xurl}
        \usepackage{setspace}
        \usepackage{fontspec}
        \setmainfont{TeX Gyre Pagella}
        \setsansfont{TeX Gyre Heros}
        \setmonofont{DejaVu Sans Mono}
        \setstretch{1.08}
        \setlength{\emergencystretch}{3em}
        \makeatletter
        \def\maxwidth{\ifdim\Gin@nat@width>\linewidth\linewidth\else\Gin@nat@width\fi}
        \def\maxheight{\ifdim\Gin@nat@height>0.82\textheight 0.82\textheight\else\Gin@nat@height\fi}
        \makeatother
        \setkeys{Gin}{width=\maxwidth,height=\maxheight,keepaspectratio}
        \captionsetup{font=small,labelfont=bf}
        \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\}}
        \pagestyle{fancy}
        \fancyhf{}
        \fancyhead[L]{\nouppercase{\leftmark}}
        \fancyhead[R]{AI LLM Red Team Handbook}
        \fancyfoot[C]{\thepage}
        \renewcommand{\headrulewidth}{0.4pt}
        \renewcommand{\footrulewidth}{0pt}
        \titleformat{\chapter}[display]
          {\normalfont\huge\bfseries}
          {\chaptertitlename\ \thechapter}
          {0.5em}
          {\Huge}
        \titlespacing*{\chapter}{0pt}{-10pt}{24pt}
        \pretocmd{\chapter}{\cleardoublepage}{}{}
        """
    ).strip() + "\n"


def build_sources() -> list[Path]:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)

    write_text(FRONTMATTER_MD, frontmatter_markdown())
    write_text(HEADER_TEX, latex_header())

    processed_files = [FRONTMATTER_MD]
    for index, filename in enumerate(CHAPTER_FILES, start=1):
        source = DOCS / filename
        text = preprocess_markdown(filename, source.read_text(encoding="utf-8"))
        output = CHAPTERS_DIR / f"{index:02d}_{filename}"
        write_text(output, text)
        processed_files.append(output)
    return processed_files


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def run_latex(cmd: list[str], cwd: Path, expected_pdf: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, check=False)
    if result.returncode != 0 and not expected_pdf.exists():
        raise SystemExit(f"LaTeX build failed: {' '.join(cmd)}")


def build_pdf() -> None:
    ensure_tool("pandoc")
    ensure_tool("xelatex")
    sources = build_sources()

    pandoc_cmd = [
        "pandoc",
        "--from=markdown+raw_html+smart+pipe_tables+task_lists+link_attributes+tex_math_dollars",
        "--standalone",
        "--top-level-division=chapter",
        "--highlight-style=tango",
        "--include-in-header",
        str(HEADER_TEX),
        "-o",
        str(OUTPUT_TEX),
    ] + [str(path) for path in sources]
    run(pandoc_cmd, ROOT)

    expected_pdf = OUTPUT_TEX.with_suffix(".pdf")
    for _ in range(2):
        run_latex(
            [
                "xelatex",
                "-interaction=nonstopmode",
                f"-output-directory={BUILD}",
                str(OUTPUT_TEX),
            ],
            ROOT,
            expected_pdf,
        )

    generated_pdf = expected_pdf
    if generated_pdf.exists():
        shutil.copy2(generated_pdf, OUTPUT_PDF)
    else:
        raise SystemExit("Expected PDF was not generated.")


if __name__ == "__main__":
    build_pdf()
