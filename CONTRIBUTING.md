# Contributing to SierraVault

Thank you for your interest in contributing to SierraVault! This guide will help you get started.

## 🎯 Ways to Contribute

### Content Improvements
- **Fix errors** — Correct factual mistakes, typos, or broken links
- **Add citations** — Find sources for uncited claims
- **Expand pages** — Add missing sections (Reception, Development, Legacy)
- **New pages** — Document missing games, designers, or studios

### Technical Contributions
- **Validation scripts** — Improve quality checking tools
- **Bug fixes** — Report or fix issues

## 📋 Before You Start

1. **Read the style guide** — See [docs/STYLE_GUIDE.md](docs/STYLE_GUIDE.md) for formatting conventions
2. **Check inclusion criteria** — See [docs/INCLUSION_CRITERIA.md](docs/INCLUSION_CRITERIA.md) for what qualifies
3. **Understand quality standards** — All pages must score 90%+ (95% for flagship games)

## 🔧 Setting Up

```bash
# Clone the repo
git clone https://github.com/d4rkwyng/sierravault.git
cd sierravault

# Open vault in Obsidian
# File → Open Vault → Select sierravault/vault folder
```

> This repository contains the vault content, templates, and site-build
> tooling only. The automated scoring/validation scripts referenced in the
> quality standards below are internal, maintainer-only tooling and aren't
> included here — see "Quality Checks" below for what to do instead.

## ✍️ Content Guidelines

### Every Claim Needs a Citation

```markdown
<!-- ❌ Bad -->
King's Quest V sold over 500,000 copies.

<!-- ✅ Good -->
King's Quest V sold over 500,000 copies.[^ref-1]

[^ref-1]: "Sierra On-Line Ships 500,000 Units of King's Quest V", *Computer Gaming World*, March 1991, p. 12.
```

### Page Structure

Every game page should have:

1. **Frontmatter** (YAML metadata)
2. **Overview** (2-3 paragraphs with citations)
3. **Story Summary** (no major spoilers)
4. **Gameplay** (interface, mechanics)
5. **Reception** (contemporary + modern reviews)
6. **Development** (team, history)
7. **Legacy** (impact, remakes)
8. **Downloads** (GOG, Steam links)
9. **Series Continuity** (prev/next links)
10. **References** (15+ citations minimum)

### Minimum Standards

| Requirement | Standard |
|-------------|----------|
| Citations | 15+ per page (20+ for flagships) |
| Duplicate URLs | None allowed |
| Structural score | ≥90% |
| LLM accuracy score | ≥90% (both Claude + GPT) |
| Flagship games | ≥95% overall |

## 🔍 Quality Checks

Before submitting, self-review your page against the Minimum Standards table
above: citation count, no duplicate reference URLs, and every `[[wiki link]]`
resolving to a real page. There's no public tool in this repo to run these
checks yourself — maintainers run automated structural scoring, dual-model
LLM accuracy scoring, and link validation against every PR as part of
review, so a careful self-review is what's expected before you open one.

## 📝 Commit Messages

Use clear, descriptive commit messages:

```
Add: [Game Name] page with [X] citations
Improve: [Game Name] citations ([old] → [new] refs)
Fix: [Game Name] broken wiki links
Update: [Designer Name] biography
Docs: Update contributing guidelines
```

## 🚀 Submitting Changes

1. **Fork** the repository
2. **Create a branch** (`git checkout -b add-game-name`)
3. **Make your changes**
4. **Run quality checks**
5. **Commit** with a clear message
6. **Push** to your fork
7. **Open a Pull Request**

### PR Checklist

- [ ] Page scores ≥90% (structural)
- [ ] All wiki links resolve
- [ ] No duplicate reference URLs
- [ ] Timestamps updated in frontmatter
- [ ] Commit message follows conventions

## 🐛 Reporting Issues

Found a problem? [Open an issue](https://github.com/d4rkwyng/sierravault/issues/new) with:

- **Page affected** (e.g., `vault/Games/King's Quest/1990 - King's Quest V.md`)
- **What's wrong** (incorrect info, broken link, missing section)
- **Evidence** (source URL if reporting factual error)

## 💬 Questions?

- Check existing [issues](https://github.com/d4rkwyng/sierravault/issues)
- Open a discussion if you're unsure about something

---

*Thank you for helping preserve Sierra's gaming legacy!* 🎮
