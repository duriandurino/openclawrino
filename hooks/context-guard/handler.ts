import { execFile } from "node:child_process";
import { promisify } from "node:util";
import path from "node:path";

const execFileAsync = promisify(execFile);

function shellEscapeSingle(value: string): string {
  return value.replace(/'/g, "");
}

function extractSessionKey(event: any): string | undefined {
  return event?.sessionKey || event?.context?.sessionKey || event?.context?.sessionEntry?.key || event?.context?.previousSessionEntry?.key;
}

function extractAgentId(event: any): string {
  const sessionKey = extractSessionKey(event);
  if (typeof sessionKey === "string" && sessionKey.startsWith("agent:")) {
    const parts = sessionKey.split(":");
    if (parts.length >= 2 && parts[1]) return parts[1];
  }
  return event?.context?.agentId || "main";
}

function buildArgs(event: any): string[] {
  const cwd = event?.context?.workspaceDir || process.cwd();
  const trigger = `${event?.type || "unknown"}:${event?.action || "event"}`;
  const pressure = event?.context?.tokenCount;
  const currentTask = event?.context?.reason || "Preserve working context before compaction or reset";
  const objective = "Maintain compact, durable working state across compaction and reset";
  const sessionKey = extractSessionKey(event);
  const agentId = extractAgentId(event);

  const args = [
    path.join(cwd, "scripts", "context_harness.py"),
    "snapshot",
    "--current-task", currentTask,
    "--objective", objective,
    "--agent-id", agentId,
    "--trigger", trigger,
    "--key-point", `event token count: ${String(pressure ?? "unknown")}`,
    "--next-step", "Resume from WORKING.md, STATE.md, OPEN_LOOPS.md, and DECISIONS.md after compaction or reset",
    "--allow-warning-snapshot",
    "--commit",
    "--push"
  ];
  if (sessionKey) {
    args.push("--session-key", sessionKey);
  }
  return args.map((x) => shellEscapeSingle(String(x)));
}

const handler = async (event: any) => {
  const eventKey = `${event?.type || ""}:${event?.action || ""}`;
  const supported = eventKey === "session:compact:before:" || event?.type === "session:compact:before" || eventKey === "command:reset" || eventKey === "command:new";
  if (!supported) return;
  const cwd = event?.context?.workspaceDir || process.cwd();
  try {
    await execFileAsync("python3", buildArgs(event), { cwd, timeout: 120000 });
  } catch (err) {
    console.error("[context-guard] harness execution failed", err);
  }
};

export default handler;
