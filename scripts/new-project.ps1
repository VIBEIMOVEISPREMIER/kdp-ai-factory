param(
  [Parameter(Mandatory=$true)][string]$Name,
  [string]$Type = "custom",
  [string]$Language = "pt-BR"
)

& .\.venv\Scripts\kdp-factory.exe new "$Name" "$Type" "$Language"
