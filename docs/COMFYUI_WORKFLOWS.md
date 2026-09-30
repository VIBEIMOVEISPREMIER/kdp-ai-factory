# ComfyUI workflows

O Factory aceita workflows JSON exportados pelo ComfyUI API format.

Use placeholders nos campos de texto:
- `{{prompt}}` para o prompt da cena.
- `{{seed}}` para uma seed fornecida pelo Factory.

Fluxo recomendado:
1. Monte/teste o workflow no ComfyUI.
2. Exporte no formato API.
3. Salve o JSON no projeto.
4. Use o endpoint/adapter ComfyUI apontando para esse arquivo.

Nenhum workflow ou modelo proprietário é baixado automaticamente.
