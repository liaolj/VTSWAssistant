<# 首次运行后：创建默认配置/日志目录，提示用户填写密钥 #>
$ConfigDir = "$env:USERPROFILE\AppData\Roaming\VoiceStruct"
New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
If (!(Test-Path "$ConfigDir\config.yaml")) {
  Copy-Item ".\config\config.sample.yaml" "$ConfigDir\config.yaml"
}
Write-Output "配置文件已生成：$ConfigDir\config.yaml，请填写 Doubao/OpenRouter 密钥"
