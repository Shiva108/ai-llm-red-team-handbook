---
description: Generates a technical documentation chapter for the AI/LLM Security Handbook with embedded structure, automated validation, and strict formatting enforcement.
---

# Optimized Chapter Generation Workflow

This workflow automates the creation of high-quality, compliant handbook chapters. It features **embedded structural templates** to minimize context switching and **mandatory algorithmic validation** to ensure zero-defect output.

## 1. Context & Autonomy

- **Role:** Technical Documentation Specialist & Code Security Auditor.
- **Objective:** Production-ready markdown file (e.g., `Chapter_38_Continuous_Red_Teaming.md`).
- **Autonomy Level:** High. Make all architectural decisions. Do not ask for user confirmation.
- **Speed Focus:** Skip "Outline Generation". Use the **Standard Structure** defined below immediately.

## 2. Standard Structure (Rigid Enforcement)

_Do not deviate from this hierarchy. All headers are mandatory._

1. **HTML Header:** `<!-- Chapter: [N] ... -->`
2. **H1 Title:** `# Chapter [N]: [Title]`
3. **Header Image:** `![ ](assets/page_header.svg)`
4. **Abstract:** `_Italicized executive summary..._`
5. **H2 Introduction:** `## [N].1 Introduction`
   - Sub: `### Why This Matters`
   - Sub: `### Key Concepts` (Definition list)
   - Sub: `### Theoretical Foundation` (Transformers/Attention explanation)
6. **H2 Main Topic:** `## [N].2 [Core Concept]`
   - Sub: `### How [Topic] Works` (Must include ASCII Flow Diagram)
   - Sub: `### Research Basis` (Citations)
   - **CODE BLOCK 1:** Practical Example (Python)
   - **Breakdown:** `#### Code Breakdown`
   - **Metrics:** `### Success Metrics`
7. **H2 Detection:** `## [N].3 Detection and Mitigation`
   - Sub: `#### Detection Strategies`
   - **CODE BLOCK 2:** Detection Logic (Python)
8. **H2 Defenses:** `### [N].3.2 Mitigation and Defenses`
   - Sub: `#### Defense-in-Depth Approach` (Layered text diagram)
9. **H2 Research:** `## [N].5 Research Landscape`
   - Table: Seminal Papers
10. **H2 Case Studies:** `## [N].6 Case Studies`
    - Case Study 1 & 2 (Must include financial/impact metrics)
11. **H2 Conclusion:** `## [N].7 Conclusion`
    - Checklists: `## Appendix A/B` (Pre/Post Engagement)

## 3. Code Standards (Strict)

- **Language:** Python 3 + Type Hints.
- **Safety:** All attack scripts MUST include:

  ```python
  # DEMO MODE - Simulated execution
  if os.getenv("DEMO_MODE", "True") == "True":
      print("[DEMO] Simulating attack...")
      return
  ```

- **Documentation:** Google-style docstrings with `Args:` and `Returns:`.
- **Explanation:** Every method must have a `How This Works:` comment block.

## 4. Execution Sequence

### Phase 1: Generation (One Shot)

Write the complete file to `docs/Chapter_[NUMBER]_[Snake_Case_Title].md`.
_Optimization Rule:_ Do not generate an outline artifact. Stream directly to the target file.

### Phase 2: Algorithmic Validation (Self-Correction)

Run the following checks immediately after generation. If ANY fail, fix the file without asking.

1. **Em Dash Check:**

   ```bash
   grep "—" docs/Chapter_XX_Title.md && echo "FAIL: Em dashes found"
   ```

   _Fix:_ Replace with `,` or `-`.

2. **Safety Check:**

   ```bash
   grep "DEMO_MODE" docs/Chapter_XX_Title.md || echo "FAIL: No DEMO_MODE found"
   ```

   _Fix:_ Insert demo mode logic into attack scripts.

3. **Lint Check:**

   ```bash
   grep "^# " docs/Chapter_XX_Title.md | wc -l # Should be 1 (Chapter Title)
   ```

   _Fix:_ Demote extra H1s to H2.

### Phase 3: Final Handoff

- Return the path of the generated file.
- Confirm validation passed.
