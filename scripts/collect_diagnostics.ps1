<# 采集日志与环境信息（自动脱敏） #>
$OutDir = "artifacts/diagnostics_$(Get-Date -Format yyyyMMdd_HHmmss)"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# 基本环境
systeminfo > "$OutDir/systeminfo.txt"
Get-ComputerInfo | Out-File "$OutDir/computerinfo.txt"

# 应用日志（示例路径）
Copy-Item -Path "logs/*.log" -Destination "$OutDir/" -ErrorAction SilentlyContinue

# 脱敏处理（简单示例：掩码 API Key）
Get-ChildItem $OutDir -Filter *.log | ForEach-Object {
  (Get-Content $_.FullName) -replace "[A-Za-z0-9_\-]{16,}", "[REDACTED]" | Set-Content $_.FullName
}

Compress-Archive -Path "$OutDir/*" -DestinationPath "$OutDir.zip" -Force
Write-Output "Diagnostics saved to $OutDir.zip"
