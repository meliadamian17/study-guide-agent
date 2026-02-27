# Study Guide Generation Guidelines

Follow these rules when generating study guides from course materials.

---

## 1. Completeness — No Detail Omitted

- **Cover every topic** from modules, pages, assignments, announcements, and files.
- **Include every definition** that appears in the course materials.
- **Capture every example** (or a representative sample with clear references to others).
- **Do not summarize away** important formulas, steps, or caveats. If it appears in the source, it belongs in the guide unless it is purely administrative (e.g., due dates without conceptual content).
- **Verify coverage** against the course structure: each module, page, and assignment should map to at least one section in the guide.

---

## 2. Diagrams — Recreate with Mermaid

- **Recreate all diagrams** from slides, textbooks, or pages using Mermaid syntax.
- Supported diagram types: flowchart, sequenceDiagram, classDiagram, stateDiagram, erDiagram, gantt, pie.
- Keep labels concise; match the structure and relationships of the original.
- After each diagram: **cite the source** (e.g., "Source: Week 3 Slides, p.12" or "Source: Textbook Ch.5, Fig.2").
- If the original cannot be fully represented in Mermaid, describe it in prose and note: "Original diagram in [source] — see for full detail."

---

## 3. Referencing Source Material

- **Always cite the source** when summarizing, paraphrasing, or quoting.
- Use a consistent format: `[Source: <location>]` — e.g., `[Source: Module 2, Page "Introduction"]`, `[Source: Assignment 1 instructions]`, `[Source: File "lecture-notes.pdf"]`.
- Paraphrasing is allowed, but must be **traceable**: a reader should be able to find the original.
- Do not present ideas as your own when they come from course materials. Attribution is required.

---

## 4. Structure Alignment

- Use the study guide **template** structure: Key Definitions, Core Concepts, Concrete Examples, Practice Questions, Diagrams, References.
- Fill every section that applies. If a section has no content for this course, state that explicitly (e.g., "No formal definitions in this module — focus on concepts below.").
- Order content to match the course flow (e.g., definitions before concepts, concepts before examples).

---

## 5. Quality Checks Before Finalizing

- [ ] Every module and page has been consulted.
- [ ] Every definition is included or explicitly noted as absent.
- [ ] Diagrams are recreated in Mermaid with source citations.
- [ ] Every summary or paraphrase has a source reference.
- [ ] Practice questions span recall, application, and synthesis.
- [ ] No critical detail from the source material has been dropped.
