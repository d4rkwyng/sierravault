import path from "path"
import { FilePath } from "./path"
import { globby } from "globby"

export function toPosixPath(fp: string): string {
  return fp.split(path.sep).join("/")
}

export async function glob(
  pattern: string,
  cwd: string,
  ignorePatterns: string[],
): Promise<FilePath[]> {
  const fps = (
    await globby(pattern, {
      cwd,
      ignore: ignorePatterns,
      // content/ is generated at build time and gitignored (lives in vault/);
      // don't let .gitignore hide it. ignorePatterns still covers .obsidian etc.
      gitignore: false,
    })
  ).map(toPosixPath)
  return fps as FilePath[]
}
