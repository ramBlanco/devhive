import { Plugin } from "@opencode/plugin"

const DEVHIVE_SKILL_PATTERNS = [
  /^devhive-/,
  /^architecture-patterns$/,
  /^backend-architect$/,
  /^backend-security-coder$/,
  /^docker-expert$/,
  /^frontend-design$/,
  /^frontend-developer$/,
  /^theme-factory$/,
]

const BUILTIN_SKILL_IDS = new Set(["opencode", "report", "customize-opencode"])

function isDevHiveSkill(id: string): boolean {
  return DEVHIVE_SKILL_PATTERNS.some((pattern) => pattern.test(id))
}

function isBuiltInSkill(id: string, path: string): boolean {
  return BUILTIN_SKILL_IDS.has(id) || path.startsWith("/builtin/")
}

function isWithinDirectory(path: string, directory: string): boolean {
  const normalizedPath = path.replaceAll("\\", "/")
  const normalizedDirectory = directory.replaceAll("\\", "/").replace(/\/$/, "")
  return normalizedPath.startsWith(`${normalizedDirectory}/`)
}

function isProjectSkill(path: string, projectRoot: string): boolean {
  return [
    `${projectRoot}/.opencode/skills`,
    `${projectRoot}/.opencode/skill`,
    `${projectRoot}/.claude/skills`,
    `${projectRoot}/.agents/skills`,
    `${projectRoot}/skills`,
  ].some((directory) => isWithinDirectory(path, directory))
}

export default Plugin.define({
  id: "devhive-skills-only",
  async setup(ctx) {
    const projectRoot = ctx.location.project.canonical

    await ctx.skill.transform((editor) => {
      for (const skill of [...editor.list()]) {
        if (isDevHiveSkill(skill.id)) continue
        if (isBuiltInSkill(skill.id, skill.path)) continue
        if (isProjectSkill(skill.path, projectRoot)) continue
        editor.remove(skill.id)
      }
    })
  },
})
