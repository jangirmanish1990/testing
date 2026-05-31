# Project context (injected memory)

Background Claude Code should keep in mind while working in this repo.

## Domain

This is a *research* tool. Quality bar is academic-adjacent: sourced claims,
balanced perspectives, explicit uncertainty. "Confidently wrong" is the worst
possible output — prefer "we couldn't find a good source for X" over guessing.

## Why multi-agent

Splitting research / writing / criticism into separate agents mirrors how a
human research team works and produces better reports than one monolithic prompt:
- The Researcher has no incentive to write nice prose, so it focuses on evidence.
- The Writer can't add facts, only arrange them.
- The Critic is adversarial by design and catches the other two's mistakes.

## Demo framing

This is a portfolio project. The code should be clean and readable enough to be
a code sample in interviews. Favor clarity over cleverness. Comment the *why*,
not the *what*.
