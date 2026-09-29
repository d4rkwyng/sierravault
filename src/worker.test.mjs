// Unit tests for the edge redirector's slug translation.
// Run: node --test src/worker.test.mjs (or `npm test`, which wires up the
// same Node test runner).
//
// Fixtures below are checked against the live site, not just hand-derived:
// the "King's Quest II+" case corresponds to the one real title in the vault
// containing a literal "+" (vault/Games/Fan Games/2002 - King's Quest II+ -
// Romancing the Stones.md), confirmed live at
// sierravault.net/games/fan-games/2002-king's-quest-ii+-romancing-the-stones.
import test from "node:test"
import assert from "node:assert/strict"
import { toQuartzSlug } from "./worker.js"

test("basic Obsidian Publish path -> Quartz slug", () => {
  assert.equal(
    toQuartzSlug("/Games/King's+Quest/1984+-+King's+Quest+-+Quest+for+the+Crown"),
    "/games/king's-quest/1984-king's-quest-quest-for-the-crown",
  )
})

test("single-segment path (no series folder)", () => {
  assert.equal(toQuartzSlug("/Designers/Roberta+Williams"), "/designers/roberta-williams")
})

test("literal '+' in a title survives, distinct from the +-for-space encoding", () => {
  // Old-style Obsidian link: the literal "+" in "II+" plus the "+" separator
  // before " - " collapse to "++" in the raw path.
  assert.equal(
    toQuartzSlug("/Games/Fan+Games/2002+-+King's+Quest+II++-+Romancing+the+Stones"),
    "/games/fan-games/2002-king's-quest-ii+-romancing-the-stones",
  )
})

test("'&' becomes '-and-'", () => {
  assert.equal(toQuartzSlug("/Games/Various/Field+%26+Stream"), "/games/various/field-and-stream")
})

test("%20-encoded spaces are normalized like literal '+'", () => {
  assert.equal(toQuartzSlug("/Games/Some%20Game%20With%20Spaces"), "/games/some-game-with-spaces")
})

test("malformed percent-encoding throws (caller must catch)", () => {
  // The fetch() handler relies on this throwing so scanner traffic with
  // invalid %-sequences falls through to static assets instead of 500ing.
  assert.throws(() => toQuartzSlug("/Games/%zz"), URIError)
})

test("fetch() falls through to ASSETS on malformed percent-encoding instead of throwing", async () => {
  const worker = (await import("./worker.js")).default
  const request = new Request("https://sierravault.net/Games/%zz")
  let assetsCalled = false
  const env = {
    ASSETS: {
      fetch: async (req) => {
        assetsCalled = true
        return new Response("ok", { status: 404 })
      },
    },
  }
  const res = await worker.fetch(request, env)
  assert.equal(assetsCalled, true)
  assert.equal(res.status, 404)
})

test("fetch() redirects a capitalized old-style path with 301", async () => {
  const worker = (await import("./worker.js")).default
  const request = new Request("https://sierravault.net/Designers/Roberta+Williams")
  const env = {
    ASSETS: { fetch: async () => new Response("should not be called", { status: 500 }) },
  }
  const res = await worker.fetch(request, env)
  assert.equal(res.status, 301)
  assert.equal(new URL(res.headers.get("location")).pathname, "/designers/roberta-williams")
})

test("fetch() leaves lowercase (already-Quartz) paths alone", async () => {
  const worker = (await import("./worker.js")).default
  const request = new Request("https://sierravault.net/games/king's-quest")
  let assetsCalled = false
  const env = {
    ASSETS: {
      fetch: async () => {
        assetsCalled = true
        return new Response("ok")
      },
    },
  }
  const res = await worker.fetch(request, env)
  assert.equal(assetsCalled, true)
  assert.equal(await res.text(), "ok")
})
