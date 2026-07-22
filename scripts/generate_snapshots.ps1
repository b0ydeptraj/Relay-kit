$commands = @(
  "accessibility",
  "manifest",
  "eval",
  "proof",
  "upgrade",
  "policy",
  "support",
  "readiness",
  "release",
  "continuity",
  "migration",
  "publish",
  "commercial",
  "pulse",
  "signal",
  "accessibility review",
  "manifest write",
  "manifest stamp",
  "manifest verify",
  "eval run",
  "eval real-world",
  "eval skill-battle",
  "eval competency-battle",
  "eval skill-weakness-report",
  "eval battle-audit",
  "eval battle-benchmark",
  "eval repo-profile",
  "eval domain-pack",
  "proof audit",
  "upgrade check",
  "upgrade plan",
  "upgrade mark-current",
  "policy check",
  "support bundle",
  "support request",
  "support triage",
  "support soak",
  "readiness check",
  "release verify",
  "release readiness",
  "continuity checkpoint",
  "continuity auto",
  "continuity rehydrate",
  "continuity handoff",
  "continuity diff-since-last",
  "migration guard",
  "publish plan",
  "publish evidence",
  "publish trail",
  "publish index-check",
  "publish status",
  "commercial dossier",
  "pulse build",
  "signal export"
)
foreach ($cmd in $commands) {
  $argsList = $cmd.Split(" ")
  $argsList += "--help"
  $fileName = $cmd.Replace(" ", "_") + "_help.txt"
  $outputPath = "tests\cli_snapshots\$fileName"
  
  $processArgs = @("relay_kit_public_cli.py") + $argsList
  
  $output = & python $processArgs 2>&1
  $output | Out-File -FilePath $outputPath -Encoding utf8
}
