# KDP AI Factory

Open-source AI publishing factory for creating, editing, illustrating, formatting, validating and preparing books for Amazon KDP.

> Official edition: the source code is open, while the official distribution uses a one-book free trial and a lifetime license after the trial.

## What it does

The Factory is designed as a modular editorial workstation for children's books, fiction, educational books, workbooks, journals, planners, notebooks, cookbooks, poetry, coloring books and custom editorial projects.

The pipeline covers briefing, outline, manuscript, revision, assets, layout, cover, KDP validation and export.

## Open-source principles

- No Docker requirement for normal Windows use.
- No mandatory paid AI API.
- Modular AI providers.
- Multiple languages.
- Visual dashboard plus CLI.
- PDF, DOCX and EPUB workflows.
- KDP-oriented validation.
- Local projects and checkpoints.
- Large AI model weights are never bundled with the repository.

## Windows installation

See [docs/INSTALL_WINDOWS.md](docs/INSTALL_WINDOWS.md).

Basic PowerShell flow:

~~~powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
kdp-factory init
kdp-factory doctor
kdp-factory start
~~~

The dashboard can be run separately from apps/dashboard:

~~~powershell
npm install
npm run dev
~~~

## Trial and licensing

The official client permits one free book per installation/machine.

After that, the official edition requires a lifetime license. The licensing layer uses a hashed machine fingerprint and a remote licensing service.

Important: open-source software cannot technically prevent a third party from modifying its own fork. The protection therefore applies to the official build and official license service. Private signing keys and payment-provider credentials must never be committed to GitHub.

Read [docs/LICENSING.md](docs/LICENSING.md).

## Payments

The planned official payment flow supports USDT on BNB Smart Chain (BSC), BNB on BNB Smart Chain, and a lifetime license price of US$50.

Official receiving address:

0x09fa433f8df884356bbb8a1afe1fb11bea3e12e5

Payment verification will validate the network, asset, destination address, amount, transaction hash and blockchain confirmation before issuing a license.

Bybit API credentials are server-only secrets. They are never shipped to clients.

## Architecture

~~~text
Windows client
   |
   +-- Dashboard / FastAPI
   +-- Editorial engine
   +-- Import / export
   +-- KDP validator
   +-- Optional Ollama
   +-- Optional ComfyUI
   |
   +-- Official licensing service
          |
          +-- License database
          +-- Payment verification
          +-- BSC on-chain verification
          +-- Bybit deposit verification
          +-- Digital license signing
~~~

## Security

Do not commit Bybit API keys, Bybit API secrets, private signing keys, production database credentials or server environment files.

Use environment variables and secret storage on the licensing server.

## Development

~~~powershell
pip install -r requirements.txt
pytest
~~~

For CLI help:

~~~powershell
kdp-factory --help
~~~

For diagnostics:

~~~powershell
kdp-factory doctor
kdp-factory models
~~~

## Project status

The repository is under active development. The native Windows path and licensing foundation are being prepared before the official payment service and cloud deployment are finalized.

## License

The final open-source license is intentionally left to the project owner to define before public release.
