# KDP AI Factory

Open-source AI publishing factory for creating, editing, illustrating, formatting, validating and preparing books for Amazon KDP.

> Official edition: this repository contains the public application. The official distribution may use a one-book free trial and a lifetime license after the trial.

## What it does

The Factory is designed as a modular editorial workstation for children's books, fiction, educational books, workbooks, journals, planners, notebooks, cookbooks, poetry, coloring books and custom editorial projects. The selected book type is intended to drive the appropriate project settings, layout and export requirements.

The pipeline covers briefing, book type, outline, manuscript, revision, assets, layout, cover, KDP validation and export.

## Publishing formats

The project is designed around two main publishing paths:

- **Print books:** interior and cover files prepared according to the selected KDP print configuration.
- **eBooks/Kindle:** digital files and image assets prepared for electronic publication, with requirements that differ from print.

KDP requirements can vary by marketplace, book type, trim size, bleed, color/interior configuration and publication format. The Factory provides preparation and validation; the final requirements shown by Amazon KDP should always be checked before publishing.

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

## Windows distribution and installation

See [docs/INSTALL_WINDOWS.md](docs/INSTALL_WINDOWS.md).

### Ready-to-use desktop build

The packaged Windows application can be distributed as a standalone executable/installer. End users do not need to install Python or Node.js just to run the packaged application.

### Development from source

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

The dashboard can be run separately from `apps/dashboard` during development:

~~~powershell
npm install
npm run dev
~~~

## Linux distribution

A Linux desktop binary can also be built from the repository. Source installation uses the Python requirements and the same `kdp-factory` CLI.

## Trial and licensing

The official client permits one free book per installation/machine.

After that, the official edition requires a lifetime license. The licensing layer uses a hashed machine fingerprint and a remote licensing service.

The public repository contains the application and license-verification client. The production licensing/payment implementation belongs in a separate private repository. See [docs/LICENSE_ARCHITECTURE.md](docs/LICENSE_ARCHITECTURE.md).

Important: open-source software cannot technically prevent a third party from modifying its own fork. The protection therefore applies to the official build and official license service. Private signing keys and payment-provider credentials must never be committed to GitHub.

Read [docs/LICENSING.md](docs/LICENSING.md).

## Payments

The official license price is **US$50 for a lifetime license**.

The customer does not have to use Bybit. A compatible wallet or exchange capable of sending the selected asset on BSC may be used.

The official payment flow supports USDT on BNB Smart Chain (BSC), BNB on BNB Smart Chain, and a lifetime license price of US$50. Customers can pay from a compatible wallet or exchange; Bybit is optional.

Official receiving address:

0x09fa433f8df884356bbb8a1afe1fb11bea3e12e5

Payment verification must validate the network, asset, destination address, eligible amount, transaction hash, uniqueness and required blockchain confirmations before issuing a license.

### Simple customer payment flow

1. Choose USDT or BNB.
2. Select the **BSC / BNB Smart Chain** network.
3. Copy the official payment address.
4. Send the required amount.
5. Paste the TXID/hash.
6. Request payment verification.
7. The server verifies the transaction directly on BSC.
8. After confirmation, the lifetime license is issued.

**Important:** the required BSC network must be shown clearly before payment. Sending an asset through the wrong network can result in loss of funds.

### Bybit

Bybit is optional and may be used by the operator for managing received crypto assets. It is not the customer's required payment platform.

Bybit is an optional operational tool for managing received crypto assets. It is not required for the customer to make a payment. Payment verification is performed directly on BNB Smart Chain (BSC).

## Architecture

~~~text
PUBLIC GITHUB REPOSITORY
   |
   +-- Dashboard / FastAPI
   +-- Editorial engine
   +-- Import / export
   +-- KDP validator
   +-- Optional Ollama
   +-- License client
   +-- Public-key verification
   |
   +------------------------------+
                                  |
                                  v
PRIVATE OFFICIAL REPOSITORY
   |
   +-- License API
   +-- Trial database
   +-- Payment verification
   +-- BSC secondary verification
   +-- Optional exchange/operational integration
   +-- License database
   +-- Private signing key
   +-- Production secrets
~~~

## Security

Do not commit exchange API keys/secrets, private signing keys, production database credentials or server environment files.

Use environment variables and secret storage on the private licensing server.

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

The native Windows path, public licensing client, official licensing API boundary, Render deployment configuration and desktop build workflows are included.

The production payment verifier is maintained in the separate private license-server repository. Real payments should only be accepted after the private service, secrets, blockchain verification and end-to-end payment tests are configured.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).


## Hybrid AI architecture

KDP AI Factory is designed to work in three modes:

1. **Local** — Ollama and ComfyUI run on the user's PC.
2. **Remote GPU** — the desktop app connects to a KDP AI Engine Server running on a GPU VPS.
3. **External API** — the user can register a paid, free, or self-hosted image API with a custom URL, endpoint, model and API key.

The desktop application detects hardware and selects a capability profile. Modest computers can remain usable in Compatibility Mode instead of being rejected solely because they lack a powerful GPU.

### Remote GPU

See vps/SETUP.md for the complete server setup. The recommended starting point for individual users is a 24 GB NVIDIA GPU such as an RTX 4090.

The Windows dashboard provides fields for the remote engine URL and token. The token is stored locally and is never displayed by the configuration endpoint.

### Image API providers

The dashboard provides generic provider fields:

- provider name
- base URL
- endpoint
- API key
- model

Providers can be paid, free, or self-hosted. Credentials are kept out of GitHub.

### Windows distribution

GitHub Actions builds the Windows executable and Inno Setup installer. The installer uses a permissive hardware gate: 64-bit Windows, 8 GB RAM and 10 GB free space are the installation baseline. GPU-heavy features are selected at runtime instead of preventing installation.

The project intentionally does not bundle third-party model weights or proprietary AI binaries.
