// Guards the vault's YAML frontmatter.
//
// build.sh runs sanitize-frontmatter.mjs, which *quarantines* (silently drops
// from the site) any page whose frontmatter js-yaml can't parse, and still
// exits 0. The usual culprit is an unquoted value containing " #": YAML treats
// that as the start of a comment, so a multi-line description like
//   description: ... Hi-Res Adventure #5, is ...
//     epic for the Apple II ...
// becomes a parse error ("bad indentation of a mapping entry") and the page
// 404s on the live site. On a single-line value it instead silently truncates
// the text at the "#". Both are caught here before they ship.
import { test } from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import yaml from "js-yaml"

const VAULT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "vault")
// Same pattern sanitize-frontmatter.mjs uses to find the frontmatter block.
const FM_RE = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/

function mdFiles(dir) {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name.startsWith(".")) continue // .obsidian etc.
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...mdFiles(p))
    else if (e.name.endsWith(".md")) out.push(p)
  }
  return out
}

function countHashes(v) {
  if (typeof v === "string") return (v.match(/#/g) || []).length
  if (Array.isArray(v)) return v.reduce((n, x) => n + countHashes(x), 0)
  if (v && typeof v === "object") return Object.values(v).reduce((n, x) => n + countHashes(x), 0)
  return 0
}

const pages = mdFiles(VAULT)
  .map((file) => ({ file, m: fs.readFileSync(file, "utf8").match(FM_RE) }))
  .filter(({ m }) => m)

test("vault has frontmatter pages to check", () => {
  assert.ok(pages.length > 100, `only found ${pages.length} pages with frontmatter`)
})

test("every page's frontmatter parses (else build.sh quarantines it off the site)", () => {
  const bad = []
  for (const { file, m } of pages) {
    try {
      yaml.load(m[1])
    } catch (e) {
      bad.push(`${path.relative(VAULT, file)}: ${e.message.split("\n")[0]}`)
    }
  }
  assert.deepEqual(
    bad,
    [],
    "unparseable frontmatter (quote values containing ' #'):\n" + bad.join("\n"),
  )
})

test("no frontmatter value is truncated by an unquoted ' #' comment", () => {
  const bad = []
  for (const { file, m } of pages) {
    let data
    try {
      data = yaml.load(m[1])
    } catch {
      continue // reported by the parse test above
    }
    // A deliberate annotation like `total_games: 7  # six games plus a remake`
    // (whitespace, '#', whitespace-or-EOL) is a real comment and fine. The
    // hazard is an unquoted value like `Hi-Res Adventure #5`, where the '#'
    // runs straight into text — so drop conventional comments before counting.
    const stripped = m[1]
      .split(/\r?\n/)
      .map((line) => line.replace(/(^|[ \t])#(?=[ \t]|$).*$/, "$1"))
      .join("\n")
    const raw = (stripped.match(/#/g) || []).length
    if (raw > countHashes(data)) bad.push(path.relative(VAULT, file))
  }
  assert.deepEqual(bad, [], "'#' in frontmatter was eaten as a YAML comment:\n" + bad.join("\n"))
})
