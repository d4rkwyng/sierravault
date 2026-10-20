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

// '#' characters in comments that can't have truncated anything: whole-line
// comments, and trailing comments after a complete value that isn't a plain
// string — a number/bool/null (`total_games: 7  # six games plus a remake`) or
// a fully quoted string. Only a trailing comment after an *unquoted string*
// value is the accidental-truncation case this test exists to catch.
function intentionalCommentHashes(fm) {
  let n = 0
  for (const line of fm.split(/\r?\n/)) {
    let comment = null
    if (/^\s*#/.test(line)) comment = line
    else {
      const t = line.match(/^\s*[A-Za-z_][\w-]*:\s+(.+?)\s+(#.*)$/)
      if (t) {
        const v = t[1]
        let complete = /^"(?:[^"\\]|\\.)*"$|^'(?:[^']|'')*'$/.test(v)
        if (!complete) {
          try {
            const parsed = yaml.load(v)
            complete = parsed === null || typeof parsed === "number" || typeof parsed === "boolean"
          } catch {}
        }
        if (complete) comment = t[2]
      }
    }
    if (comment) n += (comment.match(/#/g) || []).length
  }
  return n
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
  assert.deepEqual(bad, [], "unparseable frontmatter (quote values containing ' #'):\n" + bad.join("\n"))
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
    const raw = (m[1].match(/#/g) || []).length - intentionalCommentHashes(m[1])
    if (raw > countHashes(data)) bad.push(path.relative(VAULT, file))
  }
  assert.deepEqual(bad, [], "'#' in frontmatter was eaten as a YAML comment:\n" + bad.join("\n"))
})
